#this should ideally be a cron job, that was increasing the scope so creating an API for now.

import json
from fastapi import APIRouter
from managers.summary_service_manager import generate_summary

router = APIRouter()

@router.post("/summary_generator")
async def summary_generator(number_of_rows: int = 1):
    resp = await generate_summary(number_of_rows=number_of_rows)
    return json.dumps(resp)


@router.post("/summary_pdf_generator")
async def summary_pdf_generator(number_of_rows: int = 1):
    return await generate_summary(number_of_rows=number_of_rows, generate_pdf=True)

@router.post("/summary_generator_with_fq")
async def summary_generator_with_fq(number_of_rows: int = 1):
    return await generate_summary(number_of_rows=number_of_rows, generate_pdf=True)
