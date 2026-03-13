import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from backend.database import Base


class ImageRecord(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    original_name = Column(String, nullable=False)
    original_format = Column(String, nullable=False)
    converted_format = Column(String, nullable=True)
    original_url = Column(String, nullable=True)
    converted_url = Column(String, nullable=True)
    file_size = Column(String, nullable=True)
    converted_size = Column(String, nullable=True)
    status = Column(String, default="uploaded")  # uploaded, converting, completed, failed
    upload_date = Column(DateTime, default=datetime.utcnow)
    conversion_date = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "original_name": self.original_name,
            "original_format": self.original_format,
            "converted_format": self.converted_format,
            "original_url": self.original_url,
            "converted_url": self.converted_url,
            "file_size": self.file_size,
            "converted_size": self.converted_size,
            "status": self.status,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "conversion_date": self.conversion_date.isoformat() if self.conversion_date else None,
        }
