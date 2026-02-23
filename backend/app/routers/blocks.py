"""
Blocks API router - stores block content in MongoDB.
"""

from typing import List

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.mongodb import get_mongo
from app.core.auth import get_current_user, CurrentUser
from app.schemas import BlockSchema, BlocksSaveRequest, BlockTemplateSchema
from app.data.block_templates import BLOCK_TEMPLATES

router = APIRouter(tags=["blocks"])


@router.get("/pages/{page_id}/blocks", response_model=List[BlockSchema])
async def get_page_blocks(
    page_id: str,
    user: CurrentUser = Depends(get_current_user),
    mongo: AsyncIOMotorDatabase = Depends(get_mongo),
):
    """Get all blocks for a page, ordered by 'order' field."""
    cursor = mongo.blocks.find(
        {"page_id": page_id},
        {"_id": 0, "page_id": 0},
    ).sort("order", 1)

    blocks = await cursor.to_list(length=500)
    return blocks


@router.put("/pages/{page_id}/blocks")
async def save_page_blocks(
    page_id: str,
    data: BlocksSaveRequest,
    user: CurrentUser = Depends(get_current_user),
    mongo: AsyncIOMotorDatabase = Depends(get_mongo),
):
    """Bulk save/replace all blocks for a page."""
    # Delete existing blocks
    await mongo.blocks.delete_many({"page_id": page_id})

    # Insert new blocks
    if data.blocks:
        docs = []
        for block in data.blocks:
            doc = block.model_dump()
            doc["page_id"] = page_id
            docs.append(doc)
        await mongo.blocks.insert_many(docs)

    return {"status": "ok", "count": len(data.blocks)}


@router.get("/block-templates", response_model=List[BlockTemplateSchema])
async def get_block_templates(
    user: CurrentUser = Depends(get_current_user),
):
    """Get the block template library."""
    return BLOCK_TEMPLATES
