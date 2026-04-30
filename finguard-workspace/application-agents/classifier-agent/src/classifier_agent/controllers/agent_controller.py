from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import asyncio

from transaction_engine.classifier import classify_transaction
from ..schemas.transactions import TransactionRequest, TransactionResponseItem
from ..resources.db_service import get_db
from ..models import TransactionRecord



router = APIRouter()


@router.post("/stream/transactions", response_class=StreamingResponse)
def stream_transaction(
        transaction_request: TransactionRequest,
        #llm_service = Depends(get_llm_service), # TODO
        #http_client = Depends(get_http_client), # TODO
        db_session: "Session" = Depends(get_db),
    ):

    async def transaction_generator(descriptions):
        for description in descriptions:
            response = TransactionResponseItem(
                description=description,
                category=classify_transaction(description)
            )
            # Persist to database
            db_record = TransactionRecord(description=description, category=category)
            db_session.add(db_record)
            db_session.commit()
            db_session.refresh(db_record)
            yield {'data': response.model_dump_json()}

        yield {'type': 'done'}

    return StreamingResponse(transaction_generator(
        transaction_request.descriptions
    ), media_type="text/event-stream")