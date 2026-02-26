"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


# ========== SEO ==========

class SeoSchema(BaseModel):
    title: str = ""
    description: str = ""
    keywords: Optional[str] = None
    ogImage: Optional[str] = None
    canonicalUrl: Optional[str] = None
    noIndex: Optional[bool] = False


# ========== Blocks ==========

class BlockSettingsSchema(BaseModel):
    paddingTop: str = "60px"
    paddingBottom: str = "60px"
    backgroundColor: str = "#ffffff"
    backgroundImage: Optional[str] = None
    align: Optional[str] = "center"
    fullWidth: Optional[bool] = False
    animation: Optional[str] = None
    customClass: Optional[str] = None
    cssClass: Optional[str] = None
    anchor: Optional[str] = None
    hideOnMobile: Optional[bool] = False
    hideOnDesktop: Optional[bool] = False


class BlockSchema(BaseModel):
    id: str
    type: str
    category: str
    content: Dict[str, Any] = {}
    settings: BlockSettingsSchema = BlockSettingsSchema()
    order: int = 0


class BlockTemplateSchema(BaseModel):
    type: str
    category: str
    name: str
    description: str = ""
    thumbnail: str = ""
    defaultContent: Dict[str, Any] = {}
    defaultSettings: Dict[str, Any] = {}
    htmlTemplate: str = ""


# ========== Pages ==========

class PageResponse(BaseModel):
    id: str
    siteId: str
    title: str
    slug: str
    blocks: List[str] = []
    htmlContent: Optional[str] = None
    seo: SeoSchema = SeoSchema()
    status: str = "draft"
    isMain: bool = False
    isHomePage: Optional[bool] = False
    createdAt: str
    updatedAt: str


class PageCreateRequest(BaseModel):
    title: str
    slug: Optional[str] = None


class PageUpdateRequest(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    seo: Optional[SeoSchema] = None
    status: Optional[str] = None
    isMain: Optional[bool] = None
    isHomePage: Optional[bool] = None
    htmlContent: Optional[str] = None


# ========== Domains ==========

class DomainResponse(BaseModel):
    id: str
    siteId: Optional[str] = None
    domain: Optional[str] = None
    domainName: Optional[str] = None
    sslStatus: Optional[str] = "none"
    isPrimary: Optional[bool] = False
    isVerified: Optional[bool] = False
    createdAt: Optional[str] = None


# ========== Global Settings ==========

class GlobalSettingsSchema(BaseModel):
    fonts: Optional[Dict[str, str]] = None
    colors: Optional[Dict[str, str]] = None
    primaryColor: Optional[str] = None
    fontFamily: Optional[str] = None
    customCss: Optional[str] = None
    headScripts: Optional[str] = None
    favicon: Optional[str] = None
    headerBlockId: Optional[str] = None
    footerBlockId: Optional[str] = None


# ========== Sites ==========

class SiteResponse(BaseModel):
    id: str
    userId: str
    name: str
    description: Optional[str] = None
    subdomain: Optional[str] = None
    favicon: Optional[str] = None
    isPublished: Optional[bool] = False
    isImported: Optional[bool] = False
    globalSettings: GlobalSettingsSchema = GlobalSettingsSchema()
    domains: List[DomainResponse] = []
    pages: List[PageResponse] = []
    status: str = "draft"
    createdAt: str
    updatedAt: str


class SiteCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_imported: Optional[bool] = False


class SiteUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subdomain: Optional[str] = None
    favicon: Optional[str] = None
    globalSettings: Optional[GlobalSettingsSchema] = None


# ========== Blocks bulk save ==========

class BlocksSaveRequest(BaseModel):
    blocks: List[BlockSchema]


# ========== Health ==========

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
