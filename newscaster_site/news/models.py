from django.db import models
from django.utils import translation

# Create your models here.
class WebSource(models.Model):
    #add source id
    #source_id = models.CharField()
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    base_url = models.URLField()
    paths = models.JSONField(default=dict)
    selectors = models.JSONField(default=dict)
    custom_logic = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Web Source"
        verbose_name_plural = "Web Sources"

class Article(models.Model):
    #article metadata
    progress_stages = models.JSONField(default=list)
    current_stage = models.CharField(max_length=100, blank=True, null=True)
    source_url = models.URLField(unique=True)
    primary_category = models.CharField(max_length=100, blank=True, null=True, default=None)
    tags = models.JSONField(default=list)
    
    #article content
    raw_content = models.TextField()
    source = models.ForeignKey(WebSource, on_delete=models.CASCADE)
    title_fi = models.CharField(max_length=200)
    subject_fi = models.CharField(max_length=500)
    title_sv = models.CharField(max_length=200, blank=True, null=True)
    subject_sv = models.CharField(max_length=500, blank=True, null=True)
    title_en = models.CharField(max_length=200, blank=True, null=True)
    subject_en = models.CharField(max_length=500, blank=True, null=True)
    state_fi = models.CharField(max_length=100, blank=True, null=True)
    stage_fi = models.CharField(max_length=100, blank=True, null=True)
    state_sv = models.CharField(max_length=100, blank=True, null=True)
    stage_sv = models.CharField(max_length=100, blank=True, null=True)
    state_en = models.CharField(max_length=100, blank=True, null=True)
    stage_en = models.CharField(max_length=100, blank=True, null=True)

    #vote counts
    total_votes = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    last_voted_at = models.DateTimeField(blank=True, null=True)
    pct_yes = models.IntegerField(default=0)
    pct_undecided = models.IntegerField(default=0)
    pct_no = models.IntegerField(default=0)    
    votes_yes = models.IntegerField(default=0)
    votes_no = models.IntegerField(default=0)
    votes_undecided = models.IntegerField(default=0)

    # Structured summary fields - Finnish
    summary_proposal_details_fi = models.TextField(blank=True, null=True)
    summary_citizen_impact_fi = models.TextField(blank=True, null=True)

    # Structured summary fields - Swedish
    summary_proposal_details_sv = models.TextField(blank=True, null=True)
    summary_citizen_impact_sv = models.TextField(blank=True, null=True)

    # Structured summary fields - English
    summary_proposal_details_en = models.TextField(blank=True, null=True)
    summary_citizen_impact_en = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_fi

    def get_raw_content_reading_time(self):
        """
        Calculates the estimated reading time for the raw content.
        """
        word_count = len(self.raw_content.split())
        reading_time = round(word_count / 250)
        return {'word_count': word_count, 'reading_time': reading_time}

    @property
    def translated_title(self):
        lang = translation.get_language()
        return getattr(self, f'title_{lang}', self.title_fi)

    @property
    def translated_subject(self):
        lang = translation.get_language()
        return getattr(self, f'subject_{lang}', self.subject_fi)

    @property
    def translated_state(self):
        lang = translation.get_language()
        return getattr(self, f'state_{lang}', self.state_fi)

    @property
    def translated_stage(self):
        lang = translation.get_language()
        return getattr(self, f'stage_{lang}', self.stage_fi)

    @property
    def translated_summary_proposal_details(self):
        lang = translation.get_language()
        return getattr(self, f'summary_proposal_details_{lang}', self.summary_proposal_details_fi)

    @property
    def translated_summary_citizen_impact(self):
        lang = translation.get_language()
        return getattr(self, f'summary_citizen_impact_{lang}', self.summary_citizen_impact_fi)

    @property
    def current_stage_index(self):
        try:
            return self.progress_stages.index(self.current_stage) + 1
        except (ValueError, IndexError):
            return 0

    def get_summary_reading_time(self):
        """
        Calculates the estimated reading time for the summarized content
        in the current language.
        """
        summary_text = " ".join(filter(None, [
            self.translated_summary_proposal_details,
            self.translated_summary_citizen_impact
        ]))
        word_count = len(summary_text.split())
        reading_time = round(word_count / 250)
        return {'word_count': word_count, 'reading_time': reading_time}

    class Meta:
        ordering = ['-created_at']

class StageSummary(models.Model):
    """
    A model to store the count of articles in each stage.
    """
    stage_name = models.CharField(max_length=100, unique=True)
    article_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.stage_name} ({self.article_count})"

    class Meta:
        verbose_name = "Stage Summary"
        verbose_name_plural = "Stage Summaries"
