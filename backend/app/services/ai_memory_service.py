from sqlalchemy.orm import Session

from app.models.models import (

    Conversation,

    Message
)


# ─────────────────────────────────────────────
# CREATE CONVERSATION
# ─────────────────────────────────────────────

def create_conversation(

    db: Session,

    user_id: int,

    title: str = "New Conversation"
):

    conversation = Conversation(

        user_id=user_id,

        title=title
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    return conversation


# ─────────────────────────────────────────────
# SAVE MESSAGE
# ─────────────────────────────────────────────

def save_message(

    db: Session,

    conversation_id: int,

    role: str,

    content: str
):

    message = Message(

        conversation_id=
            conversation_id,

        role=role,

        content=content
    )

    db.add(message)

    db.commit()

    db.refresh(message)

    return message


# ─────────────────────────────────────────────
# GET CONVERSATION MESSAGES
# ─────────────────────────────────────────────

def get_conversation_messages(

    db: Session,

    conversation_id: int
):

    messages = (

        db.query(Message)

        .filter(

            Message.conversation_id ==
            conversation_id
        )

        .order_by(
            Message.created_at.asc()
        )

        .all()
    )

    formatted_messages = []

    for message in messages:

        formatted_messages.append({

            "role": message.role,

            "content": message.content
        })

    return formatted_messages


# ─────────────────────────────────────────────
# GET USER CONVERSATIONS
# ─────────────────────────────────────────────

def get_user_conversations(

    db: Session,

    user_id: int
):

    conversations = (

        db.query(Conversation)

        .filter(

            Conversation.user_id ==
            user_id
        )

        .order_by(
            Conversation.created_at.desc()
        )

        .all()
    )

    return conversations