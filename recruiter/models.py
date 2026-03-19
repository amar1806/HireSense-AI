from django.db import models
from django.contrib.auth.models import User
import json

class ResumeAnalysis(models.Model):
    """Store resume analysis results for each user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    match_score = models.FloatField()
    ats_score = models.FloatField()
    skills = models.JSONField(default=list)  # List of skills
    gaps = models.JSONField(default=list)   # Skill gaps
    recommended = models.JSONField(default=list)  # Recommended skills
    negatives = models.JSONField(default=list)   # Resume weaknesses
    improvements = models.JSONField(default=list)  # Suggested improvements
    pdf_path = models.CharField(max_length=255, null=True, blank=True)  # Path to generated PDF
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.file_name}"
