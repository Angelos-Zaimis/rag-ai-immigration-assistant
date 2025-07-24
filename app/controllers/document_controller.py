from services.documents.document_service import DocumentService


class DocumentController:

    def __init__(self):
        self.service = DocumentService()


    async def upload_pdf(self, file_path: str):
        return await self.service.handle_upload_pdf_file(file_path)

