from django.db import models

# Create your models here.


class Lesson(models.Model):
    # User ID retrieved from the Core service cookies
    user_id = models.IntegerField() 
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (User: {self.user_id})"

class Word(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='words')
    term = models.CharField(max_length=100) # English word
    definition = models.TextField()        # Persian translation
    
    # --- 8-Tick Logic ---
    # Current review day (from 1 to 8)
    current_day = models.IntegerField(default=0) 
    
    # Stores ticks and crosses as an 8-character string (e.g., '11010000')
    review_history = models.CharField(max_length=8, default='00000000')
    
    # Final learning status (True if 6 ticks are achieved)
    is_learned = models.BooleanField(default=False)
    
    # To prevent multiple reviews on the same day
    last_review_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.term