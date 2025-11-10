"""
文献管理 API
"""
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse
from app.core.database import get_db
from app.core.response import Response, PageData
from app.core.response_builder import ResponseBuilder, PageDataBuilder
from app.core.exceptions import LiteratureException, NotFoundException
from app.models.schemas import (
    LiteratureQueryRequest,
    LiteratureResponse,
    LiteratureDetailResponse,
    HealthResponse
)
from app.services.literature_service import literature_service
from app.services.file_service import file_service
from app.services.ai_service import ai_service
from app.config import settings

router = APIRouter(prefix="/literature", tags=["文献管理"])


@router.get("/health", response_model=Response[HealthResponse])
async def health_check():
    """健康检查"""
    return ResponseBuilder.ok(
        data=HealthResponse(status="ok", message="服务正常运行"),
        message="健康检查通过"
    )


@router.post("/page", response_model=Response[PageData[LiteratureResponse]])
async def page_query(
    query_params: LiteratureQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    分页查询文献列表
    """
    try:
        literatures, total = await literature_service.page_query(db, query_params)
        
        # 转换为响应模型
        records = [literature_service.to_response(lit) for lit in literatures]
        
        # 使用建造者模式构建分页数据
        page_data = PageDataBuilder.from_query_result(
            records=records,
            total=total,
            page_num=query_params.pageNum,
            page_size=query_params.pageSize
        )
        
        return ResponseBuilder.ok(data=page_data, message="查询成功")
    
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"查询失败: {str(e)}", code=500)


@router.get("/{literature_id}", response_model=Response[LiteratureDetailResponse])
async def get_literature_detail(
    literature_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取文献详情
    """
    try:
        literature = await literature_service.get_literature_by_id(db, literature_id)
        
        if not literature:
            raise NotFoundException("文献不存在")
        
        detail = literature_service.to_detail_response(literature)
        
        return ResponseBuilder.ok(data=detail, message="查询成功")
    
    except NotFoundException as e:
        return ResponseBuilder.not_found(message=e.message)
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"查询失败: {str(e)}", code=500)


@router.get("/{literature_id}/download")
async def download_literature(
    literature_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    下载文献文件
    """
    try:
        literature = await literature_service.get_literature_by_id(db, literature_id)
        
        if not literature:
            raise HTTPException(status_code=404, detail="文献不存在")
        
        # 构建完整文件路径
        file_path = os.path.join(settings.UPLOAD_DIR, literature.file_path)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 返回文件
        return FileResponse(
            path=file_path,
            filename=literature.original_name,
            media_type="application/octet-stream"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.post("/generate-guide")
async def generate_reading_guide(
    file: UploadFile = File(...),
    apiKey: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    上传文献并生成阅读指南（SSE流式响应）
    """
    literature_id = None
    file_full_path = None
    
    async def event_generator():
        nonlocal literature_id, file_full_path
        
        try:
            # 1. 保存文件
            yield {
                "event": "progress",
                "data": "正在保存文件..."
            }
            
            file_full_path, file_relative_path, file_size, file_type = await file_service.save_file(file)
            
            # 2. 提取文件内容
            yield {
                "event": "progress",
                "data": "正在解析文件内容..."
            }
            
            content = await file_service.extract_content(file_full_path, file_type)
            content_length = len(content)
            
            # 3. 创建文献记录（初始状态为处理中）
            yield {
                "event": "progress",
                "data": "正在创建文献记录..."
            }
            
            literature = await literature_service.create_literature(
                db=db,
                original_name=file.filename,
                file_path=file_relative_path,
                file_size=file_size,
                file_type=file_type,
                content_length=content_length,
                status=0  # 处理中
            )
            literature_id = literature.id
            await db.commit()
            
            # 4. 生成阅读指南（流式）
            yield {
                "event": "start",
                "data": "开始生成阅读指南..."
            }
            
            reading_guide_parts = []
            
            async for message in ai_service.generate_reading_guide_stream(content, apiKey):
                msg_type = message.get("type")
                msg_data = message.get("data", "")
                
                if msg_type == "content":
                    reading_guide_parts.append(msg_data)
                    yield {
                        "event": "content",
                        "data": msg_data
                    }
                elif msg_type == "progress":
                    yield {
                        "event": "progress",
                        "data": msg_data
                    }
            
            # 5. 保存完整的阅读指南
            reading_guide = "".join(reading_guide_parts)
            
            # 6. 从阅读指南中提取标签和描述
            yield {
                "event": "progress",
                "data": "正在提取标签和描述..."
            }
            
            tags, description = await ai_service.extract_tags_and_description(
                reading_guide,
                apiKey
            )
            
            await literature_service.update_literature(
                db=db,
                literature_id=literature_id,
                reading_guide=reading_guide,
                tags=tags,
                description=description,
                status=1  # 已完成
            )
            await db.commit()
            
            # 7. 发送完成消息
            yield {
                "event": "complete",
                "data": "阅读指南生成完成！"
            }
        
        except LiteratureException as e:
            # 更新状态为失败
            if literature_id:
                try:
                    await literature_service.update_literature(
                        db=db,
                        literature_id=literature_id,
                        status=2  # 失败
                    )
                    await db.commit()
                except:
                    pass
            
            yield {
                "event": "error",
                "data": e.message
            }
        
        except Exception as e:
            # 更新状态为失败
            if literature_id:
                try:
                    await literature_service.update_literature(
                        db=db,
                        literature_id=literature_id,
                        status=2  # 失败
                    )
                    await db.commit()
                except:
                    pass
            
            # 清理文件
            if file_full_path and os.path.exists(file_full_path):
                try:
                    file_service.delete_file(file_full_path)
                except:
                    pass
            
            yield {
                "event": "error",
                "data": f"生成失败: {str(e)}"
            }
    
    return EventSourceResponse(event_generator())

