# app/services/ai_memory_service.py

from sqlalchemy.orm import Session
from app.models.models import Conversation, Message
from typing import List, Dict, Any, Optional
from datetime import datetime

# ─────────────────────────────────────────────
# CREATE CONVERSATION
# ─────────────────────────────────────────────

def create_conversation(
    db: Session,
    user_id: int,
    title: str = "New Conversation"
) -> Conversation:
    """
    Create a new conversation for a user.
    """
    try:
        conversation = Conversation(
            user_id=user_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            report_generated=False
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return conversation
    
    except Exception as e:
        db.rollback()
        print(f"Error creating conversation: {e}")
        raise

# ─────────────────────────────────────────────
# SAVE MESSAGE - FIXED
# ─────────────────────────────────────────────

def save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """
    Save a message to the conversation.
    """
    try:
        # Validate role
        if role not in ["user", "assistant", "system"]:
            raise ValueError(f"Invalid role: {role}. Must be 'user', 'assistant', or 'system'")
        
        # Create message with updated_at
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()  # ← FIXED: Added updated_at
        )
        
        db.add(message)
        
        # Update conversation's updated_at timestamp
        db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).update({"updated_at": datetime.utcnow()})
        
        db.commit()
        db.refresh(message)
        
        return message
    
    except Exception as e:
        db.rollback()
        print(f"Error saving message: {e}")
        raise

# ─────────────────────────────────────────────
# GET CONVERSATION MESSAGES
# ─────────────────────────────────────────────

def get_conversation_messages(
    db: Session,
    conversation_id: int,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get all messages from a conversation.
    Returns formatted list of messages with role and content.
    """
    try:
        query = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())
        
        if limit is not None:
            query = query.limit(limit)
        
        if offset is not None:
            query = query.offset(offset)
        
        messages = query.all()
        
        formatted_messages = []
        for message in messages:
            formatted_messages.append({
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "updated_at": message.updated_at.isoformat() if message.updated_at else None
            })
        
        return formatted_messages
    
    except Exception as e:
        print(f"Error retrieving conversation messages: {e}")
        return []

# ─────────────────────────────────────────────
# GET CONVERSATION BY ID
# ─────────────────────────────────────────────

def get_conversation(
    db: Session,
    conversation_id: int
) -> Optional[Conversation]:
    """
    Get a specific conversation by ID.
    """
    try:
        return db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
    except Exception as e:
        print(f"Error retrieving conversation: {e}")
        return None

# ─────────────────────────────────────────────
# GET USER CONVERSATIONS
# ─────────────────────────────────────────────

def get_user_conversations(
    db: Session,
    user_id: int,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Conversation]:
    """
    Get all conversations for a user.
    """
    try:
        query = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc())
        
        if limit is not None:
            query = query.limit(limit)
        
        if offset is not None:
            query = query.offset(offset)
        
        return query.all()
    
    except Exception as e:
        print(f"Error retrieving user conversations: {e}")
        return []

# ─────────────────────────────────────────────
# UPDATE CONVERSATION TITLE
# ─────────────────────────────────────────────

def update_conversation_title(
    db: Session,
    conversation_id: int,
    new_title: str
) -> Optional[Conversation]:
    """
    Update the title of a conversation.
    """
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if conversation:
            conversation.title = new_title
            conversation.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(conversation)
            return conversation
        
        return None
    
    except Exception as e:
        db.rollback()
        print(f"Error updating conversation title: {e}")
        raise

# ─────────────────────────────────────────────
# MARK REPORT GENERATED
# ─────────────────────────────────────────────

def mark_report_generated(
    db: Session,
    conversation_id: int
) -> bool:
    """
    Mark a conversation as having a generated report.
    """
    try:
        result = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).update({
            "report_generated": True,
            "updated_at": datetime.utcnow()
        })
        
        db.commit()
        return result > 0
    
    except Exception as e:
        db.rollback()
        print(f"Error marking report as generated: {e}")
        return False

# ─────────────────────────────────────────────
# DELETE CONVERSATION
# ─────────────────────────────────────────────

def delete_conversation(
    db: Session,
    conversation_id: int
) -> bool:
    """
    Delete a conversation and all its messages.
    """
    try:
        # Delete all messages first
        db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).delete()
        
        # Delete the conversation
        result = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).delete()
        
        db.commit()
        return result > 0
    
    except Exception as e:
        db.rollback()
        print(f"Error deleting conversation: {e}")
        return False

# ─────────────────────────────────────────────
# GET CONVERSATION SUMMARY
# ─────────────────────────────────────────────

def get_conversation_summary(
    db: Session,
    conversation_id: int
) -> Dict[str, Any]:
    """
    Get a summary of the conversation including message count and metadata.
    """
    try:
        conversation = get_conversation(db, conversation_id)
        if not conversation:
            return {}
        
        messages = get_conversation_messages(db, conversation_id)
        
        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
            "message_count": len(messages),
            "report_generated": conversation.report_generated
        }
    
    except Exception as e:
        print(f"Error getting conversation summary: {e}")
        return {}

# ─────────────────────────────────────────────
# GET CONVERSATION HISTORY (Alias for get_conversation_messages)
# ─────────────────────────────────────────────

def get_conversation_history(
    db: Session,
    conversation_id: int,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Alias for get_conversation_messages to maintain compatibility.
    """
    return get_conversation_messages(db, conversation_id, limit)

# ─────────────────────────────────────────────
# SAVE MULTIPLE MESSAGES
# ─────────────────────────────────────────────

def save_messages_batch(
    db: Session,
    conversation_id: int,
    messages: List[Dict[str, str]]
) -> List[Message]:
    """
    Save multiple messages in a conversation.
    """
    try:
        saved_messages = []
        now = datetime.utcnow()
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            
            if role not in ["user", "assistant", "system"]:
                continue
            
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                created_at=now,
                updated_at=now
            )
            db.add(message)
            saved_messages.append(message)
        
        # Update conversation's updated_at
        db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).update({"updated_at": now})
        
        db.commit()
        
        for msg in saved_messages:
            db.refresh(msg)
        
        return saved_messages
    
    except Exception as e:
        db.rollback()
        print(f"Error saving batch messages: {e}")
        return []

# ─────────────────────────────────────────────
# GET LAST N MESSAGES
# ─────────────────────────────────────────────

def get_last_messages(
    db: Session,
    conversation_id: int,
    n: int = 10
) -> List[Dict[str, Any]]:
    """
    Get the last N messages from a conversation.
    """
    try:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(n).all()
        
        # Reverse to get chronological order
        messages.reverse()
        
        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in messages
        ]
    
    except Exception as e:
        print(f"Error getting last messages: {e}")
        return []