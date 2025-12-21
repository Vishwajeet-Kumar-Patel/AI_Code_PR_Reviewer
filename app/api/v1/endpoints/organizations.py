"""
Organization/Multi-tenancy API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.db.models import User, Organization, OrganizationMember
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import re


router = APIRouter(prefix="/organizations", tags=["Organizations"])


class OrganizationCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    plan: str = "free"


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    plan: Optional[str] = None


class MemberInvite(BaseModel):
    user_id: int
    role: str = "member"


class MemberRoleUpdate(BaseModel):
    role: str


@router.post("/")
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new organization"""
    
    # Validate slug format
    if not re.match(r"^[a-z0-9-]+$", org_data.slug):
        raise HTTPException(
            status_code=400,
            detail="Slug must contain only lowercase letters, numbers, and hyphens"
        )
    
    # Check if slug already exists
    existing = db.query(Organization).filter(
        Organization.slug == org_data.slug
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Organization slug already exists")
    
    # Create organization
    organization = Organization(
        name=org_data.name,
        slug=org_data.slug,
        description=org_data.description,
        plan=org_data.plan,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    # Add creator as owner
    member = OrganizationMember(
        organization_id=organization.id,
        user_id=current_user.id,
        role="owner",
        created_at=datetime.utcnow()
    )
    
    db.add(member)
    db.commit()
    
    return {
        "message": "Organization created successfully",
        "organization": {
            "id": organization.id,
            "name": organization.name,
            "slug": organization.slug,
            "plan": organization.plan
        }
    }


@router.get("/")
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all organizations the user is a member of"""
    
    memberships = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == current_user.id
    ).all()
    
    organizations = []
    for membership in memberships:
        org = db.query(Organization).filter(
            Organization.id == membership.organization_id
        ).first()
        
        if org:
            organizations.append({
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "role": membership.role,
                "plan": org.plan,
                "member_count": len(org.members)
            })
    
    return {"organizations": organizations}


@router.get("/{org_id}")
async def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organization details"""
    
    # Check membership
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    organization = db.query(Organization).filter(
        Organization.id == org_id
    ).first()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return {
        "id": organization.id,
        "name": organization.name,
        "slug": organization.slug,
        "description": organization.description,
        "avatar_url": organization.avatar_url,
        "plan": organization.plan,
        "max_repositories": organization.max_repositories,
        "max_members": organization.max_members,
        "is_active": organization.is_active,
        "created_at": organization.created_at.isoformat(),
        "member_count": len(organization.members),
        "your_role": membership.role
    }


@router.patch("/{org_id}")
async def update_organization(
    org_id: int,
    update_data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update organization (admin/owner only)"""
    
    # Check if user is admin or owner
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.role.in_(["owner", "admin"])
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    organization = db.query(Organization).filter(
        Organization.id == org_id
    ).first()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Update fields
    if update_data.name:
        organization.name = update_data.name
    if update_data.description:
        organization.description = update_data.description
    if update_data.avatar_url:
        organization.avatar_url = update_data.avatar_url
    if update_data.plan and membership.role == "owner":
        organization.plan = update_data.plan
    
    organization.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(organization)
    
    return {"message": "Organization updated successfully"}


@router.delete("/{org_id}")
async def delete_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete organization (owner only)"""
    
    # Check if user is owner
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.role == "owner"
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Only owners can delete organizations")
    
    organization = db.query(Organization).filter(
        Organization.id == org_id
    ).first()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Delete all memberships
    db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id
    ).delete()
    
    # Delete organization
    db.delete(organization)
    db.commit()
    
    return {"message": "Organization deleted successfully"}


@router.get("/{org_id}/members")
async def list_members(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List organization members"""
    
    # Check membership
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    members = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id
    ).all()
    
    member_list = []
    for member in members:
        user = db.query(User).filter(User.id == member.user_id).first()
        if user:
            member_list.append({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": member.role,
                "joined_at": member.created_at.isoformat()
            })
    
    return {"members": member_list}


@router.post("/{org_id}/members")
async def invite_member(
    org_id: int,
    invite_data: MemberInvite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite a member to organization (admin/owner only)"""
    
    # Check permissions
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.role.in_(["owner", "admin"])
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if user exists
    user = db.query(User).filter(User.id == invite_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == invite_data.user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    # Check member limit
    org = db.query(Organization).filter(Organization.id == org_id).first()
    current_members = len(org.members)
    
    if current_members >= org.max_members:
        raise HTTPException(status_code=400, detail="Member limit reached")
    
    # Create membership
    new_member = OrganizationMember(
        organization_id=org_id,
        user_id=invite_data.user_id,
        role=invite_data.role,
        invited_by=current_user.id,
        created_at=datetime.utcnow()
    )
    
    db.add(new_member)
    db.commit()
    
    return {"message": "Member invited successfully"}


@router.patch("/{org_id}/members/{user_id}")
async def update_member_role(
    org_id: int,
    user_id: int,
    role_data: MemberRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update member role (owner only)"""
    
    # Check if current user is owner
    requester_membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.role == "owner"
    ).first()
    
    if not requester_membership:
        raise HTTPException(status_code=403, detail="Only owners can change roles")
    
    # Find member to update
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == user_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Validate role
    if role_data.role not in ["owner", "admin", "member"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    member.role = role_data.role
    db.commit()
    
    return {"message": "Member role updated successfully"}


@router.delete("/{org_id}/members/{user_id}")
async def remove_member(
    org_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove member from organization"""
    
    # Check permissions (owner/admin can remove, or user can remove themselves)
    if user_id != current_user.id:
        membership = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.role.in_(["owner", "admin"])
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Find member to remove
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == user_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Prevent removing last owner
    if member.role == "owner":
        owner_count = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.role == "owner"
        ).count()
        
        if owner_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last owner"
            )
    
    db.delete(member)
    db.commit()
    
    return {"message": "Member removed successfully"}
