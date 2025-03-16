from django.db import models

class PDFDocument(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='pdfs/')  # Файли будуть зберігатися в media/pdfs/
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class ChatMessage(models.Model): # Модель для зберігання повідомлень чату
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self): # Повертаємо текстове представлення моделі
        return self.message
