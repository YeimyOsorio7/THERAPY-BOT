import sys
import os
import json
from typing import List, Dict, Any

# Add parent directory to path to import ChromaService
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.src.orquestador.chroma_data_base.chroma import ChromaService, ChromaConfig


class MentalHealthDataUploader:
    """
    Clase para cargar datos de salud mental a ChromaDB.
    Maneja trastornos, diferenciales, screenings, respuestas y expresiones coloquiales.
    """
    
    def __init__(self):
        self.chroma_service = ChromaService(ChromaConfig())
        
    def prepare_disorder_documents(self, disorders: List[Dict[str, Any]]) -> tuple:
        """Prepara documentos de trastornos para ChromaDB."""
        texts = []
        metadatas = []
        ids = []
        
        for disorder in disorders:
            # Crear texto descriptivo rico para embeddings
            text_parts = [
                f"Disorder: {disorder['disorder']}",
                f"ICD-10: {', '.join(disorder['icd10'])}",
                f"Synonyms: {', '.join(disorder['synonyms'])}",
                f"Key Criteria: {disorder['key_criteria']}",
                f"Duration: {disorder['duration_threshold']}",
                f"Typical Onset: {disorder['typical_onset_age']}",
                f"Risk Factors: {', '.join(disorder['risk_factors'])}",
                f"Comorbidity: {', '.join(disorder['comorbidity'])}",
                f"Red Flags: {', '.join(disorder['red_flags'])}",
                f"Suicide Risk: {disorder['suicide_risk_level']}",
                f"Urgent Referral: {', '.join(disorder['urgent_referral_criteria'])}"
            ]
            
            texts.append(" | ".join(text_parts))
            metadatas.append({
                "type": "disorder",
                "disorder_id": disorder['id'],
                "disorder_name": disorder['disorder'],
                "icd10": json.dumps(disorder['icd10']),
                "suicide_risk": disorder['suicide_risk_level'],
                "synonyms": json.dumps(disorder['synonyms'])
            })
            ids.append(f"disorder_{disorder['id']}")
            
        return texts, metadatas, ids
    
    def prepare_screening_documents(self, screenings: List[Dict[str, Any]]) -> tuple:
        """Prepara documentos de screening para ChromaDB."""
        texts = []
        metadatas = []
        ids = []
        
        for screening in screenings:
            text_parts = [
                f"Screening for: {screening['objective']}",
                f"Synonyms: {', '.join(screening['synonyms'])}",
                f"Questions: {' '.join(screening['screening_questions'])}",
                f"Positive Indicators: {', '.join(screening['positive_indicators'])}",
                f"Key Differentials: {', '.join(screening['key_differentials'])}",
                f"Suicide Risk Note: {screening['suicide_risk_note']}",
                f"Escalation: {' '.join(screening['escalation'])}"
            ]
            
            texts.append(" | ".join(text_parts))
            metadatas.append({
                "type": "screening",
                "screening_id": screening['id'],
                "objective": screening['objective'],
                "synonyms": json.dumps(screening['synonyms']),
                "questions": json.dumps(screening['screening_questions'])
            })
            ids.append(f"screening_{screening['id']}")
            
        return texts, metadatas, ids
    
    def prepare_response_templates(self, responses: List[Dict[str, Any]]) -> tuple:
        """Prepara plantillas de respuesta para ChromaDB."""
        texts = []
        metadatas = []
        ids = []
        
        for response in responses:
            text_parts = [
                f"Response Type: {response['type']}",
                f"Objective: {response['objective']}",
                f"Templates: {' | '.join(response['template'])}",
                f"When to Use: {', '.join(response['when_to_use'])}",
                f"Safety Notes: {', '.join(response['safety_notes'])}"
            ]
            
            texts.append(" | ".join(text_parts))
            metadatas.append({
                "type": "response_template",
                "template_id": response['id'],
                "response_type": response['type'],
                "objective": response['objective'],
                "when_to_use": json.dumps(response['when_to_use'])
            })
            ids.append(f"response_{response['id']}")
            
        return texts, metadatas, ids
    
    def prepare_colloquial_expressions(self, expressions: List[Dict[str, Any]]) -> tuple:
        """Prepara expresiones coloquiales para ChromaDB."""
        texts = []
        metadatas = []
        ids = []
        
        for expr in expressions:
            text_parts = [
                f"Colloquial Term: {expr['term']}",
                f"Variants: {', '.join(expr['variants'])}",
                f"Possible Intentions: {', '.join(expr['possible_intentions'])}",
                f"Clues: {', '.join(expr['clues'])}",
                f"Red Flags: {', '.join(expr['red_flags'])}",
                f"Suggested Questions: {', '.join(expr['suggested_questions'])}"
            ]
            
            texts.append(" | ".join(text_parts))
            metadatas.append({
                "type": "colloquial_expression",
                "expression_id": expr['id'],
                "term": expr['term'],
                "variants": json.dumps(expr['variants']),
                "possible_intentions": json.dumps(expr['possible_intentions'])
            })
            ids.append(f"colloquial_{expr['id']}")
            
        return texts, metadatas, ids
    
    def upload_all_data(self, data_dict: Dict[str, List[Dict[str, Any]]]):
        """
        Carga todos los datos a ChromaDB en colecciones separadas.
        
        Args:
            data_dict: Diccionario con claves 'disorders', 'screenings', 'responses', 'colloquial'
        """
        # Colección de trastornos
        if 'disorders' in data_dict:
            print(f"Uploading {len(data_dict['disorders'])} disorders...")
            texts, metadatas, ids = self.prepare_disorder_documents(data_dict['disorders'])
            self.chroma_service.upsert_texts(
                texts=texts,
                name_collection="mental_health_disorders",
                metadatas=metadatas,
                ids=ids
            )
            print("✓ Disorders uploaded successfully")
        
        # Colección de screenings
        if 'screenings' in data_dict:
            print(f"\nUploading {len(data_dict['screenings'])} screenings...")
            texts, metadatas, ids = self.prepare_screening_documents(data_dict['screenings'])
            self.chroma_service.upsert_texts(
                texts=texts,
                name_collection="mental_health_screenings",
                metadatas=metadatas,
                ids=ids
            )
            print("✓ Screenings uploaded successfully")
        
        # Colección de respuestas
        if 'responses' in data_dict:
            print(f"\nUploading {len(data_dict['responses'])} response templates...")
            texts, metadatas, ids = self.prepare_response_templates(data_dict['responses'])
            self.chroma_service.upsert_texts(
                texts=texts,
                name_collection="mental_health_responses",
                metadatas=metadatas,
                ids=ids
            )
            print("✓ Response templates uploaded successfully")
        
        # Colección de expresiones coloquiales
        if 'colloquial' in data_dict:
            print(f"\nUploading {len(data_dict['colloquial'])} colloquial expressions...")
            texts, metadatas, ids = self.prepare_colloquial_expressions(data_dict['colloquial'])
            self.chroma_service.upsert_texts(
                texts=texts,
                name_collection="mental_health_colloquial",
                metadatas=metadatas,
                ids=ids
            )
            print("✓ Colloquial expressions uploaded successfully")


def main():
    """Función principal para ejecutar la carga de datos."""
    
    # Datos de trastornos principales
    disorders_main = [
        {
            "id": "major_dep",
            "disorder": "Major Depressive Disorder",
            "icd10": ["F32.x","F33.x"],
            "synonyms": ["major depression","depressive episode"],
            "key_criteria": "≥5 symptoms for 2 weeks; includes depressed mood or loss of interest.",
            "duration_threshold": "≥2 weeks",
            "typical_onset_age": "Adolescence-young adult",
            "risk_factors": ["family history", "childhood trauma", "chronic stress", "medical illnesses"],
            "comorbidity": ["anxiety", "substance abuse", "borderline personality disorder"],
            "red_flags": ["suicidal ideation", "suicide plan", "psychosis"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["active ideation with a plan", "recent attempt", "concomitant psychosis"]
        },
        {
            "id": "gad",
            "disorder": "Generalized Anxiety Disorder",
            "icd10": ["F41.1"],
            "synonyms": ["GAD","persistent anxiety","excessive worry"],
            "key_criteria": 
            "Excessive worry for ≥6 months, difficult to control; with physical symptoms (restlessness, fatigue, muscle tension, sleep problems).",
            "duration_threshold": "≥6 months",
            "typical_onset_age": "Late childhood / early adulthood",
            "risk_factors": ["family history", "inhibited personality", "stressful events"],
            "comorbidity": ["depression", "other anxiety disorders", "substance abuse"],
            "red_flags": ["severe insomnia", "suicidal ideation"],
            "suicide_risk_level": "Moderate",
            "urgent_referral_criteria": ["if severe depression is present", "concurrent suicidal ideation"]
        },
        {
            "id": "panic",
            "disorder": "Panic Disorder",
            "icd10": ["F41.0"],
            "synonyms": ["panic crisis","panic attacks"],
            "key_criteria": "Recurrent and unexpected attacks, with persistent concern about future attacks and changes in behavior.",
            "duration_threshold": "≥1 month with persistent symptoms",
            "typical_onset_age": "Adolescence-young adult",
            "risk_factors": ["history of trauma", "childhood abuse", "smoking"],
            "comorbidity": ["agoraphobia", "depression", "bipolar disorder"],
            "red_flags": ["very frequent attacks", "suicidal ideation due to hopelessness"],
            "suicide_risk_level": "Moderate-High",
            "urgent_referral_criteria": ["if suicidal ideation is present", "incapacitating symptoms"]
        },
        {
            "id": "ptsd",
            "disorder": "Post-Traumatic Stress Disorder",
            "icd10": ["F43.1"],
            "synonyms": ["PTSD","post traumatic stress"],
            "key_criteria": "Exposure to trauma, re-experiencing, avoidance, cognitive/mood alterations, hyperarousal. Duration >1 month.",
            "duration_threshold": "≥1 month",
            "typical_onset_age": "Any age after a traumatic event",
            "risk_factors": ["prolonged violence", "lack of social support", "childhood trauma"],
            "comorbidity": ["depression", "substance abuse", "generalized anxiety"],
            "red_flags": ["suicidal ideation", "self-destructive behaviors", "severe dissociation"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["active ideation", "recent trauma with crisis"]
        },
        {
            "id": "bipolar_I",
            "disorder": "Bipolar I Disorder",
            "icd10": ["F31.x"],
            "synonyms": ["bipolar type I","mania"],
            "key_criteria": "Manic episodes ≥1 week with elevated/irritable mood and increased energy. May alternate with depressive episodes.",
            "duration_threshold": "≥1 week (mania)",
            "typical_onset_age": "Adolescence-young adult",
            "risk_factors": ["genetic inheritance", "early onset", "substance use"],
            "comorbidity": ["anxiety", "substance abuse", "ADHD"],
            "red_flags": ["suicidal ideation in depressive phases", "high-risk behaviors in mania"],
            "suicide_risk_level": "Very high",
            "urgent_referral_criteria": ["severe manic episode", "suicidal or homicidal risk"]
        },
        {
            "id": "schizophrenia",
            "disorder": "Schizophrenia",
            "icd10": ["F20.x"],
            "synonyms": ["psychosis","schizophrenic disorder"],
            "key_criteria": "Delusions, hallucinations, disorganized speech or behavior, negative symptoms. Duration ≥6 months.",
            "duration_threshold": "≥6 months",
            "typical_onset_age": "Late adolescence-young adult",
            "risk_factors": ["family history", "perinatal complications", "cannabis use in adolescence"],
            "comorbidity": ["depression", "anxiety", "substance abuse"],
            "red_flags": ["command hallucinations", "severe agitation", "dangerous behavior"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["if risk of harm to self/others", "acute psychosis"]
        },
        {
            "id": "adhd",
            "disorder": "Attention-Deficit/Hyperactivity Disorder",
            "icd10": ["F90.x"],
            "synonyms": ["ADHD","hyperactivity"],
            "key_criteria": "Persistent inattention and hyperactivity-impulsivity, onset before age 12, present in ≥2 contexts.",
            "duration_threshold": "≥6 months",
            "typical_onset_age": "Childhood",
            "risk_factors": ["genetic factors", "prenatal exposure to tobacco/alcohol", 
            "low birth weight"],
            "comorbidity": ["oppositional defiant disorder", "anxiety", "depression"],
            "red_flags": ["severe school failure", "risk-taking behaviors"],
            "suicide_risk_level": "Low-Moderate",
            "urgent_referral_criteria": ["if there is associated suicidal ideation or substance use"]
        },
        {
            "id": "suicide",
            "disorder": "Suicide Risk / Suicidal Ideation",
            "icd10": ["R45.8","X60-X84"],
            "synonyms": ["suicidal ideation","suicidal behavior"],
            "key_criteria": "Recurrent thoughts of death, ideation with a plan, previous attempt.",
            "duration_threshold": "variable",
            "typical_onset_age": "any age",
            "risk_factors": ["history of attempts", "severe psychiatric disorders", "social isolation"],
            "comorbidity": ["depression", "bipolar disorder", "PTSD", "substance abuse"],
            "red_flags": ["active ideation", "detailed plan", "access to means"],
            "suicide_risk_level": "Critical",
            
            "urgent_referral_criteria": ["any active ideation with a plan", "recent attempt", "high imminent risk"]
        },
        {
            "id": "dysthymia",
            "disorder": "Persistent Depressive Disorder (Dysthymia)",
            "icd10": ["F34.1"],
            "synonyms": ["dysthymia","chronic depression"],
            "key_criteria": "Depressed mood for most of the day, present for ≥2 years, with at least 2 additional depressive symptoms.",
            "duration_threshold": "≥2 years",
            "typical_onset_age": "Early adolescence or young adulthood",
            "risk_factors": ["family history of depression", "early traumas", "personality with negative affectivity"],
            "comorbidity": ["generalized anxiety disorder", "substance abuse", "personality disorders"],
            "red_flags": ["chronic suicidal ideation", "severe functional impairment"],
            "suicide_risk_level": "Moderate-High",
            "urgent_referral_criteria": ["active suicidal ideation", "extreme functional failure"]
        },
        {
            "id": "social_anxiety",
            "disorder": "Social Anxiety Disorder (Social Phobia)",
            "icd10": ["F40.1"],
            "synonyms": ["social phobia","social anxiety"],
            "key_criteria": "Intense and persistent fear of social situations where one might be evaluated, leading to avoidance or significant distress.",
            "duration_threshold": "≥6 months",
            "typical_onset_age": "Adolescence",
            "risk_factors": ["inhibited temperament", "history of bullying", "family models of anxiety"],
            "comorbidity": ["depression", "alcohol abuse", "other anxiety disorders"],
            "red_flags": ["extreme social isolation", "dropping out of school"],
            "suicide_risk_level": "Moderate",
            "urgent_referral_criteria": ["if there is associated suicidal ideation"]
        },
        {
            "id": "specific_phobia",
            "disorder": "Specific Phobia",
            "icd10": ["F40.2"],
            "synonyms": ["irrational fear","simple phobia"],
            "key_criteria": "Marked, excessive, and irrational fear of a specific object or situation, with persistent avoidance.",
            "duration_threshold": "≥6 months",
            "typical_onset_age": "Childhood or adolescence",
            "risk_factors": ["traumatic events", "vicarious learning (from family)", "behavioral inhibition"],
            "comorbidity": ["generalized anxiety", "depression"],
            "red_flags": ["avoidance that limits essential functions"],
            "suicide_risk_level": "Low",
            "urgent_referral_criteria": ["if it leads to total isolation or associated depression"]
        },
        {
            "id": "ocd",
            "disorder": "Obsessive-Compulsive Disorder",
            "icd10": ["F42"],
            "synonyms": ["OCD","obsessions and compulsions"],
            "key_criteria": "Presence of obsessions (intrusive, unwanted thoughts) and/or compulsions (repetitive behaviors) that are time-consuming and impair functioning.",
            "duration_threshold": "variable, usually chronic",
            "typical_onset_age": "Adolescence or young adult",
            "risk_factors": ["family history", "high neuroticism", "stressful life events"],
            "comorbidity": ["major depression", "anxiety disorders", "Tics/Tourette's"],
            "red_flags": ["suicidal ideation secondary to obsessions", "severe functional disability"],
            "suicide_risk_level": "Moderate",
            "urgent_referral_criteria": ["if compulsions interfere with basic needs", "if obsessions include self-harm"]
        },
        {
            "id": "adjustment_disorder",
            "disorder": "Adjustment Disorder",
            "icd10": ["F43.2"],
            "synonyms": ["stress reaction","difficult adjustment"],
            "key_criteria": "Emotional or behavioral symptoms in response to an identifiable stressor, within 3 months of its onset.",
            "duration_threshold": "Up to 6 months after the stressor",
            "typical_onset_age": "Any age",
            "risk_factors": ["adverse life events", "lack of social support", "history of emotional vulnerability"],
            "comorbidity": ["anxiety", "depression", "substance abuse"],
            "red_flags": ["suicidal ideation", "high-risk behaviors"],
            "suicide_risk_level": "Moderate",
            "urgent_referral_criteria": ["if there is suicidal risk associated with the stressor"]
        },
        {
            "id": "insomnia",
            "disorder": "Insomnia Disorder",
            "icd10": ["F51.0"],
            "synonyms": ["chronic insomnia","difficulty sleeping"],
            "key_criteria": "Difficulty initiating or maintaining sleep, or early-morning awakening, with significant distress or impairment.",
            "duration_threshold": "≥3 nights per week for ≥3 months",
            "typical_onset_age": "Adult",
            "risk_factors": ["chronic stress", "depression", "anxiety", "substance use"],
            "comorbidity": ["major depression", "generalized anxiety", "substance use disorder"],
            
            "red_flags": ["insomnia with suicidal ideation", "extreme exhaustion"],
            "suicide_risk_level": "Moderate",
            "urgent_referral_criteria": ["if insomnia is accompanied by severe depression or suicide risk"]
        },
        {
            "id": "asd",
            "disorder": "Autism Spectrum Disorder",
            "icd10": ["F84.x"],
            "synonyms": ["ASD","autism"],
            "key_criteria": "Persistent deficits in social communication and interaction; restricted, repetitive patterns of behavior, interests, or activities.",
            "duration_threshold": "symptoms present in early stages",
            "typical_onset_age": "Early childhood",
            "risk_factors": ["genetic factors", "advanced parental age", "perinatal complications"],
            "comorbidity": ["ADHD", "anxiety disorders", "depressive disorder"],
            "red_flags": ["developmental regression", "self-harm"],
            "suicide_risk_level": "Moderate (higher in high-functioning ASD with associated depression)",
            "urgent_referral_criteria": ["if self-harm or suicidal ideation is present"]
        },
        {
            "id": "oppositional_defiant",
            "disorder": "Oppositional Defiant Disorder",
            "icd10": ["F91.3"],
            "synonyms": ["ODD","oppositionality"],
            "key_criteria": "A pattern of angry/irritable mood, argumentative/defiant behavior, or vindictiveness for ≥6 months.",
            "duration_threshold": "≥6 months",
            "typical_onset_age": "Childhood",
            "risk_factors": ["inadequate parenting practices", "conflict-ridden family environments", "school rejection"],
            "comorbidity": ["ADHD", "conduct disorders", "anxiety"],
            "red_flags": ["severe aggressive behaviors", "risk of evolving into conduct disorder"],
            "suicide_risk_level": "Low-Moderate",
            "urgent_referral_criteria": ["if severe violence or suicidal ideation is present"]
        },
        {
            "id": "eating_disorder",
            "disorder": "Eating Disorders",
            "icd10": ["F50.x"],
            "synonyms": ["anorexia nervosa","bulimia nervosa","binge-eating disorder"],
            "key_criteria": "Persistent disturbance in eating or eating-related behavior that affects health or functioning.",
            "duration_threshold": "variable by subtype",
            "typical_onset_age": "Adolescence-young adult",
            "risk_factors": ["sociocultural pressure", "perfectionism", "history of trauma or abuse"],
            "comorbidity": ["depression", "anxiety", "OCD"],
            
            "red_flags": ["severe weight loss", "frequent purging behaviors", "suicidal ideation"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["critically low BMI", "suicide risk or severe purging"]
        },
        {
            "id": "somatic_disorder",
            "disorder": "Somatic Symptom Disorder",
            "icd10": ["F45.1"],
            "synonyms": ["somatic disorder","psychosomatic disorder"],
            "key_criteria": "One or more distressing somatic symptoms with excessive associated thoughts, feelings, or behaviors.",
            "duration_threshold": "≥6 months",
            "typical_onset_age": "Adolescence or adulthood",
            "risk_factors": ["low health education", "chronic medical illnesses", "high anxiety"],
            "comorbidity": ["anxiety", "depression", "hypochondriasis"],
            "red_flags": ["incapacitating symptoms", "excessive help-seeking behavior"],
            "suicide_risk_level": "Moderate (due to hopelessness)",
            "urgent_referral_criteria": ["if distress leads to suicidal ideation"]
        },
        {
            "id": "alcohol",
            "disorder": "Alcohol Use Disorder",
            "icd10": ["F10.x"],
            "synonyms": ["alcoholism","problematic alcohol use","alcohol dependence"],
            "key_criteria": "A problematic pattern of use with impairment: loss of control, intense craving, role failures, use in risky situations, tolerance/withdrawal. Severity based on # of criteria in 12 months.",
            "duration_threshold": "≥12 months (2–3 mild; 4–5 moderate; ≥6 severe)",
            "typical_onset_age": "Late adolescence–young adulthood",
            "risk_factors": ["family history", "trauma/chronic stress", "high accessibility", "depressive/anxious comorbidity"],
            "comorbidity": ["depression", "anxiety", "bipolar disorder", "PTSD"],
            "red_flags": ["severe withdrawal symptoms (delirium tremens)", "repeated failed attempts to quit", "suicidal ideation"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["complicated withdrawal", "severe intoxication", "suicide/violence risk"]
        },
        {
            "id": "cannabis",
            "disorder": "Cannabis Use Disorder",
            "icd10": ["F12.x"],
            "synonyms": ["problematic cannabis use","marijuana"],
            "key_criteria": "A problematic pattern with impairment: loss of control, use despite consequences, time spent, interpersonal/work problems; sometimes induced anxiety/psychosis.",
            "duration_threshold": "≥12 months",
            "typical_onset_age": "Adolescence",
            "risk_factors": ["early onset", "consuming peers", "stress", "psychotic vulnerability"],
            "comorbidity": ["anxiety", "depression", "psychosis", "ADHD"],
            "red_flags": ["psychotic symptoms during use", "school dropout", "daily morning use"],
            "suicide_risk_level": "Moderate (↑ with depression/psychosis)",
            "urgent_referral_criteria": ["induced psychosis", "suicide risk/severe agitation"]
        },
        {
            "id": "cocaine",
            "disorder": "Cocaine Use Disorder",
            "icd10": ["F14.x"],
            "synonyms": ["cocaine use","cocaine dependence"],
            "key_criteria": "A problematic pattern with intense craving, failure in obligations, risky use, social problems; risk of psychosis/cardiac arrest.",
            "duration_threshold": "≥12 months",
            "typical_onset_age": "Young adulthood",
            "risk_factors": ["recreational contexts", "impulsivity", "ADHD/borderline PD comorbidity", "trauma"],
            "comorbidity": ["anxiety", "depression", "personality disorders", "other SUDs"],
            "red_flags": ["cardiac/neurological symptoms", "stimulant psychosis", "high-risk behaviors"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["acute psychosis", "severe cardiac signs", "suicide/violence risk"]
        },
        {
            "id": "stimulants",
            "disorder": "Stimulant Use Disorder (amphetamines/methamphetamine)",
            "icd10": ["F15.x"],
            "synonyms": ["amphetamine use","methamphetamine","tusi (context dependent)"],
            "key_criteria": "A problematic pattern with hyperactivation, insomnia, weight loss, compulsive use; high risk of psychosis and dangerous behaviors.",
            "duration_threshold": "≥12 months",
            "typical_onset_age": "Late adolescence–young adulthood",
            "risk_factors": ["recreational environments", "sleep deprivation", "trauma/stress", "impulsivity"],
            "comorbidity": ["ADHD", "anxiety", "depression", "psychosis"],
            "red_flags": ["hyperthermia/dehydration", "psychosis", "agitation with risk of harm"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["severe psychosis/agitation", "acute medical complications", "suicide risk"]
        },
        {
            "id": "opioids",
            "disorder": "Opioid Use Disorder",
            "icd10": ["F11.x"],
            "synonyms": ["heroin use","opioid analgesics","opioid dependence"],
            "key_criteria": "A problematic pattern with craving, tolerance/withdrawal, use despite harm; risk of overdose and depressed respiration.",
            "duration_threshold": "≥12 months",
            "typical_onset_age": "Young adulthood",
            "risk_factors": ["medical exposure to opioids", "chronic pain", "family history", "socioeconomic deprivation"],
            "comorbidity": ["depression", "anxiety", "PTSD", "other SUDs"],
            "red_flags": ["current/past overdose", "use with benzodiazepines/alcohol", "apnea/deep somnolence"],
            "suicide_risk_level": "Very high",
            "urgent_referral_criteria": ["overdose", "complicated withdrawal", "suicide risk", "pregnancy with active use"]
        },
        {
            "id": "sedatives_hypnotics",
            "disorder": "Sedative, Hypnotic, or Anxiolytic Use Disorder (e.g., benzodiazepines)",
            "icd10": ["F13.x"],
            "synonyms": ["benzodiazepine use","hypnotics","anxiolytics"],
            "key_criteria": "A problematic pattern with tolerance/withdrawal; risk of falls, cognitive impairment, and respiratory depression if combined with alcohol/opioids.",
            "duration_threshold": "≥12 months",
            "typical_onset_age": "Adulthood",
            "risk_factors": ["chronic anxiety/insomnia", "polypharmacy", "advanced age"],
            "comorbidity": ["anxiety", "depression", "other SUDs"],
            "red_flags": ["withdrawal with seizure risk", "combined use with depressants", "confusion, falls"],
            "suicide_risk_level": "High (especially in poly-use and depression)",
            "urgent_referral_criteria": ["severe withdrawal", "overdose/poly-use", "suicide risk"]
        },
        {
            "id": "tobacco",
            "disorder": "Tobacco (Nicotine) Use Disorder",
            "icd10": ["F17.x"],
            "synonyms": ["smoking","nicotine use","dependent vaping"],
            "key_criteria": "A problematic pattern with dependence and withdrawal; high reinforcement; impact on cardiovascular/respiratory health.",
            "duration_threshold": "≥12 months",
            "typical_onset_age": "Adolescence",
            "risk_factors": ["smoking peers", "stress", "co-occurrence with other substances", "low risk perception"],
            "comorbidity": ["anxiety", "depression", "other SUDs"],
            "red_flags": ["use upon waking", "repeated failed quit attempts", "associated respiratory disease"],
            "suicide_risk_level": "Low-Moderate (↑ with depression/poly-use)",
            "urgent_referral_criteria": ["if coexisting suicidal ideation or high-risk poly-use"]
        },
        {
            "id": "inhalants",
            "disorder": "Inhalant Use Disorder",
            "icd10": ["F18.x"],
            "synonyms": ["solvents","glues","aerosols"],
            "key_criteria": "A problematic pattern with use of volatile solvents; dizziness/euphoria, neurological damage, risk of sudden death from hypoxia/arrhythmias.",
            "duration_threshold": "≥12 months",
            "typical_onset_age": "Early adolescence",
            "risk_factors": ["household accessibility", "contexts of social vulnerability", "lack of supervision"],
            "comorbidity": ["ADHD", "oppositional defiant disorder", "depression"],
            "red_flags": ["loss of consciousness", "neurological signs", "use in enclosed spaces"],
            "suicide_risk_level": "Moderate (↑ due to impairment and risk contexts)",
            "urgent_referral_criteria": ["respiratory/neurological compromise", "use with other depressants", "suicide risk"]
        },
        {
            "id": "prolonged_grief",
            "disorder": "Prolonged Grief Disorder (DSM-5-TR) / Persistent Complex Bereavement Disorder",
            "icd10": ["Z63.4"],
            "synonyms": ["complicated grief","pathological grief"],
            "key_criteria": "Intense yearning/emotional pain for the deceased with persistent longing, difficulty accepting the death, marked avoidance, and functional impairment.",
            "duration_threshold": "≥12 months in adults (≥6 months in children/adolescents)",
            "typical_onset_age": "After a significant loss",
            "risk_factors": ["sudden/violent death", "limited support", "depressive/anxious history", "dependence on the relationship"],
            "comorbidity": ["depression", "GAD", "PTSD"],
            "red_flags": ["marked hopelessness", "suicidal ideation focused on reuniting with the deceased"],
            "suicide_risk_level": "Moderate-High",
            "urgent_referral_criteria": ["active ideation with a plan", "severe self-neglect"]
        },
        {
            "id": "bpd",
            "disorder": "Borderline Personality Disorder",
            "icd10": ["F60.3"],
            "synonyms": ["BPD","borderline"],
            "key_criteria": "A pattern of affective and interpersonal instability, unstable self-image, impulsivity, efforts to avoid abandonment, self-harm.",
            "duration_threshold": "Persistent pattern since early adulthood",
            "typical_onset_age": "Adolescence–early adulthood",
            "risk_factors": ["childhood trauma/abuse", "family instability", "impulsivity traits"],
            "comorbidity": ["depression", "SUD", "PTSD", "Eating Disorders"],
            "red_flags": ["self-harm/attempts", "high-risk impulsivity"],
            "suicide_risk_level": "Very high",
            "urgent_referral_criteria": ["ideation/plan/means", "recent self-harm", "severe agitation"]
        },
        {
            "id": "brief_psychosis",
            "disorder": "Brief Psychotic Disorder",
            "icd10": ["F23"],
            "synonyms": ["brief psychotic episode"],
            "key_criteria": "Sudden onset of delusions, hallucinations, or disorganized speech (±catatonia), with full recovery.",
            "duration_threshold": "1 day to <1 month",
            "typical_onset_age": "Late adolescence–young adulthood",
            "risk_factors": ["acute stress", "psychotic vulnerability", "postpartum"],
            "comorbidity": ["anxiety", "depression"],
            "red_flags": ["command hallucinations", "dangerous behavior"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["risk to self/others", "inability for self-care"]
        },
        {
            "id": "catatonia",
            "disorder": "Catatonia (specifier/associated entity)",
            "icd10": ["F20.2","F06.1"],
            "synonyms": ["catatonic syndrome"],
            "key_criteria": "≥3 signs: stupor, mutism, negativism, bizarre postures, rigidity, mannerisms, echolalia/echopraxia, agitation not influenced by external stimuli.",
            "duration_threshold": "Hours–days",
            "typical_onset_age": "Variable (psychosis, mood disorders, medical conditions)",
            "risk_factors": ["affective or psychotic episodes", "NMS/medication", "neurological conditions"],
            "comorbidity": ["schizophrenia", "bipolar disorder", "major depression", "medical condition"],
            "red_flags": ["dehydration/malnutrition", "prolonged immobility", "hyperthermia"],
            "suicide_risk_level": "High (acute medical risks)",
            "urgent_referral_criteria": ["immediate medical emergency", "life-threatening risk"]
        },
        {
            "id": "depersonalization",
            "disorder": "Depersonalization/Derealization Disorder",
            "icd10": ["F48.1"],
            "synonyms": ["depersonalization","derealization"],
            "key_criteria": "Persistent/recurrent experiences of detachment from self or surroundings, with intact reality testing and significant distress.",
            "duration_threshold": "Weeks–months (variable)",
            "typical_onset_age": "Adolescence–young adult",
            "risk_factors": ["intense stress", "anxiety/panic", "trauma"],
            "comorbidity": ["anxiety", "depression", "panic"],
            "red_flags": ["depersonalization with suicidal ideation due to distress"],
            "suicide_risk_level": "Moderate (secondary to hopelessness)",
            "urgent_referral_criteria": ["active ideation", "extreme functional impairment"]
        },
        {
            "id": "dissociative_amnesia",
            "disorder": "Dissociative Amnesia (± Fugue)",
            "icd10": ["F44.0","F44.1"],
            "synonyms": ["psychogenic amnesia","dissociative fugue"],
            "key_criteria": "Inability to recall important autobiographical information (usually traumatic), not explained by ordinary forgetting.",
            "duration_threshold": "Minutes–months (variable)",
            "typical_onset_age": "Adolescence–adulthood",
            "risk_factors": ["trauma", "childhood abuse", "severe stress"],
            "comorbidity": ["PTSD", "depression", "anxiety"],
            "red_flags": ["disorientation in unknown contexts", "risk of victimization"],
            "suicide_risk_level": "Moderate",
            "urgent_referral_criteria": ["risk to personal safety", "suicidal ideation"]
        },
        {
            "id": "conversion",
            "disorder": "Functional Neurological Symptom Disorder (Conversion Disorder)",
            "icd10": ["F44.4","F44.7","F44.9"],
            "synonyms": ["conversion disorder","functional neurological symptoms"],
            "key_criteria": "Neurological symptoms (motor/sensory deficits, non-epileptic seizures) incompatible with a recognized neurological disease.",
            "duration_threshold": "Variable",
            "typical_onset_age": "Adolescence–adulthood",
            "risk_factors": ["stress/trauma", "vicarious learning", "concurrent medical illness"],
            "comorbidity": ["anxiety", "depression", "somatic"],
            "red_flags": ["falls/injuries from episodes", "use of multiple emergency services"],
            "suicide_risk_level": 
            "Low-Moderate",
            "urgent_referral_criteria": ["rule out acute medical causes", "risk of physical harm"]
        },
        {
            "id": "delusional_disorder",
            "disorder": "Delusional Disorder",
            "icd10": ["F22"],
            "synonyms": ["non-bizarre paranoia"],
            "key_criteria": "One or more delusions for ≥1 month without other prominent psychotic symptoms; relatively preserved functioning.",
            "duration_threshold": "≥1 month",
            "typical_onset_age": "Middle age",
            "risk_factors": ["social isolation", "migration/cultural stress", "psychotic vulnerability"],
            "comorbidity": ["depression", "anxiety"],
            "red_flags": ["jealous-type delusions with risk of violence", "self-harm from somatic ideas"],
            "suicide_risk_level": "Moderate",
            "urgent_referral_criteria": ["risk to others", "self-harm derived from the delusion"]
        },
        {
            "id": "schizoaffective",
            "disorder": "Schizoaffective Disorder",
            "icd10": ["F25.x"],
            "synonyms": ["affective psychosis"],
            "key_criteria": "Psychotic symptoms with a major mood episode and ≥2 weeks of psychosis without prominent affective symptoms.",
            "duration_threshold": "≥1 month (chronic/episodic pattern)",
            "typical_onset_age": "Late adolescence–young adulthood",
            "risk_factors": ["family history of psychosis/mood", "early onset"],
            "comorbidity": ["SUD", "anxiety", "metabolic risk from drugs"],
            "red_flags": ["suicidal ideation in depressive phases", "agitation/homicidal ideation"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["acute psychosis", "suicidal/violent risk"]
        },
        {
            "id": "peripartum_psychosis",
            "disorder": "Brief Psychotic Episode with Peripartum Onset",
            "icd10": ["F23 (peripartum specifier)"],
            "synonyms": ["postpartum psychosis"],
            "key_criteria": "Onset during pregnancy or within 4 weeks postpartum with delusions/hallucinations, disorganization, or catatonia; abrupt course.",
            "duration_threshold": "Days–weeks",
            "typical_onset_age": "Peripartum",
            "risk_factors": ["history of bipolar/psychosis", "sleep deprivation", "perinatal stress"],
            "comorbidity": ["mood disorders", "anxiety"],
            "red_flags": ["infanticidal/suicidal ideation", "severe disorganization"],
            "suicide_risk_level": "Very high (risk to mother and baby)",
            "urgent_referral_criteria": ["immediate psychiatric emergency", "protection of the newborn"]
        },
        {
            "id": "pd_antisocial",
            "disorder": "Antisocial Personality Disorder",
            "icd10": ["F60.2"],
            "synonyms": ["dissocial personality","APD"],
            "key_criteria": "A pattern of disregard for/violation of rights; impulsivity, deceitfulness, irresponsibility, aggressiveness. ≥18 years old with evidence of conduct disorder before age 15.",
            "duration_threshold": "Stable pattern since adolescence",
            "typical_onset_age": "Adolescence",
            "risk_factors": ["child abuse/neglect", "violent environments", "substance use", "impulsivity traits"],
            "comorbidity": ["SUD", "ADHD", "depression", "other PDs"],
            "red_flags": ["violence", "criminal behavior", "lack of remorse"],
            "suicide_risk_level": "Moderate-High (impulsivity and SUD)",
            "urgent_referral_criteria": ["risk of harm to others", "suicidal ideation/plan with poly-use"]
        },
        {
            "id": "pd_avoidant",
            "disorder": "Avoidant Personality Disorder",
            "icd10": ["F60.6"],
            "synonyms": ["avoidant personality","AvPD"],
            "key_criteria": "Social inhibition, feelings of inadequacy, hypersensitivity to negative evaluation; avoids relationships for fear of rejection.",
            "duration_threshold": "Early onset and persistent course",
            "typical_onset_age": "Adolescence",
            "risk_factors": ["inhibited temperament", "bullying", "early social rejection"],
            "comorbidity": ["depression", "social anxiety", "GAD"],
            "red_flags": ["extreme isolation", "school/work dropout"],
            "suicide_risk_level": "Low-Moderate (↑ if depression is present)",
            "urgent_referral_criteria": ["suicidal ideation associated with isolation"]
        },
        {
            "id": "pd_dependent",
            "disorder": "Dependent Personality Disorder",
            "icd10": ["F60.7"],
            "synonyms": ["dependent personality","DPD"],
            "key_criteria": "Excessive need to be taken care of; submissiveness, difficulty making decisions, fear of separation.",
            "duration_threshold": "Persistent pattern",
            "typical_onset_age": "Young adult",
            "risk_factors": ["anxious attachment", "parental overprotection", "loss events"],
            "comorbidity": ["depression", "anxiety", "other cluster C PDs"],
            "red_flags": ["risk of exploitation", "self-neglect due to submissiveness"],
            "suicide_risk_level": "Moderate (threat/fear of abandonment)",
            "urgent_referral_criteria": ["suicidal ideation upon imminent separation"]
        },
        {
            "id": "pd_obsessive_compulsive",
            "disorder": "Obsessive-Compulsive Personality Disorder",
            "icd10": ["F60.5"],
            "synonyms": ["OCPD","anankastic traits"],
            "key_criteria": "Perfectionism and mental/interpersonal control at the expense of flexibility; rules, order, excessive scrupulousness.",
            "duration_threshold": "Chronic pattern",
            "typical_onset_age": "Young adult",
            "risk_factors": ["rigid environments", "perfectionistic traits", "family history"],
            "comorbidity": ["depression", "anxiety", "OCD (differential)"],
            "red_flags": ["severe work impairment due to perfectionism"],
            "suicide_risk_level": "Low-Moderate (↑ if functional failure + depression)",
            "urgent_referral_criteria": ["suicidal ideation due to perceived failure"]
        },
        {
            "id": "did",
            "disorder": "Dissociative Identity Disorder",
            "icd10": ["F44.81","F44.8"],
            "synonyms": ["multiple personalities","DID"],
            "key_criteria": "≥2 identity states with marked discontinuity of self; amnesic gaps; distress/impairment.",
            "duration_threshold": "Months–years",
            "typical_onset_age": "Childhood (recognized in adolescence/adulthood)",
            "risk_factors": ["chronic childhood trauma", "abuse", "limited social support"],
            "comorbidity": ["PTSD", "depression", "SUD", "borderline PD"],
            "red_flags": ["self-harm", "fugue episodes", "lost time"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["self-harming behavior/active ideation", "severe disorganization"]
        },
        {
            "id": "separation_anxiety",
            "disorder": "Separation Anxiety Disorder",
            "icd10": ["F93.0"],
            "synonyms": ["separation anxiety","SAD"],
            "key_criteria": "Excessive fear concerning separation from attachment figures with somatic complaints, school avoidance, and catastrophic worries.",
            "duration_threshold": "≥4 weeks in children (≈6 months in adults)",
            "typical_onset_age": "Childhood; also in adults",
            "risk_factors": ["anxious attachment", "actual losses", "overprotection"],
            "comorbidity": ["generalized anxiety", "depression", "selective mutism"],
            "red_flags": ["persistent school refusal", "incapacitating somatic symptoms"],
            "suicide_risk_level": "Low-Moderate",
            "urgent_referral_criteria": ["if suicidal ideation due to forced separation"]
        },
        {
            "id": "selective_mutism",
            "disorder": "Selective Mutism",
            "icd10": ["F94.0"],
            "synonyms": ["situational mutism"],
            "key_criteria": "Consistent failure to speak in specific social situations despite speaking in others; interferes with educational/social achievement.",
            "duration_threshold": "≥1 month (not just first month of school)",
            "typical_onset_age": "Early childhood",
            "risk_factors": ["social anxiety", "inhibited temperament", "histories of stress"],
            "comorbidity": ["social anxiety", "SAD"],
            "red_flags": ["mutism with extreme withdrawal", "suspicion of abuse"],
            "suicide_risk_level": "Low",
            "urgent_referral_criteria": ["if coexisting suicidal ideation or maltreatment"]
        },
        {
            "id": "tourette_tics",
            "disorder": "Tourette's Syndrome / Tic Disorders",
            "icd10": ["F95.2","F95.1","F95.0"],
            "synonyms": ["chronic motor/vocal tics","Tourette's"],
            "key_criteria": "Multiple motor and vocal tics (Tourette's) or a single chronic tic; onset before age 18; fluctuating.",
            "duration_threshold": "≥1 year (chronic)",
            "typical_onset_age": "Childhood (6–7 years)",
            "risk_factors": ["genetics", "associated ADHD/OCD", "exacerbating stress"],
            "comorbidity": ["ADHD", "OCD", "anxiety"],
            "red_flags": ["self-harm from complex tics", "severe bullying/isolation"],
            "suicide_risk_level": "Low-Moderate (↑ if depression/bullying)",
            "urgent_referral_criteria": ["tics with physical risk", "suicidal ideation due to bullying"]
        },
        {
            "id": "conduct_disorder",
            "disorder": "Conduct Disorder",
            "icd10": ["F91.x"],
            "synonyms": ["dissocial conduct","CD"],
            "key_criteria": "A repetitive pattern of violating norms/rights: aggression, property destruction, deceitfulness/theft, serious rule violations.",
            "duration_threshold": "≥12 months (≥1 criterion in 6 months)",
            "typical_onset_age": "Late childhood–adolescence",
            "risk_factors": ["maltreatment/neglect", "conflict-ridden family", "delinquent peers", "APD in adult role models"],
            "comorbidity": ["ADHD", "depression", "SUD"],
            "red_flags": ["cruelty/weapons/fire-setting", "chronic truancy"],
            "suicide_risk_level": "Moderate-High (impulsivity + SUD)",
            "urgent_referral_criteria": ["violence/weapons", "risk to others"]
        },
        {
            "id": "dmdd",
            "disorder": "Disruptive Mood Dysregulation Disorder (DMDD)",
            "icd10": ["F34.81","F34.8"],
            "synonyms": ["childhood mood dysregulation","severe chronic irritability"],
            "key_criteria": "Severe recurrent temper outbursts inconsistent with developmental level, with a persistently irritable mood between episodes (≥12 months, ≥2 contexts).",
            "duration_threshold": "≥12 months without intervals >3 months without symptoms",
            "typical_onset_age": "Onset before age 10 (diagnosis 6–18)",
            "risk_factors": ["history of early irritability", "family stress", "anxious/depressive comorbidity"],
            "comorbidity": ["ADHD", "anxiety", "depression (not bipolar)"],
            "red_flags": ["aggression towards people/objects", "repeated school expulsions"],
            "suicide_risk_level": "Moderate (↑ with depression/SUD)",
            "urgent_referral_criteria": ["risk of harm to self/others", "active suicidal ideation"]
        },
        {
            "id": "peripartum_dep",
            "disorder": "Major Depressive Episode with Peripartum Onset",
            "icd10": ["F32.x","F33.x","F53.0"],
            "synonyms": ["postpartum depression","peripartum depression"],
            "key_criteria": "Depressive symptoms starting during pregnancy or within the first 4 weeks postpartum; anhedonia, guilt, fatigue, insomnia/hypersomnia, suicidal thoughts.",
            "duration_threshold": "≥2 weeks",
            "typical_onset_age": "Pregnancy or early postpartum",
            "risk_factors": ["previous peripartum history", "bipolar disorder", "lack of support", "sleep deprivation"],
            "comorbidity": ["anxiety", "postpartum OCD", "peripartum psychosis"],
            "red_flags": ["suicidal/infanticidal ideation", "inability to care for the newborn"],
            "suicide_risk_level": "Very high (risk to mother and baby)",
            "urgent_referral_criteria": ["active ideation with plan", "psychosis", "risk to newborn"]
        },
        {
            "id": "pmdd",
            "disorder": "Premenstrual Dysphoric Disorder",
            "icd10": ["N94.3"],
            "synonyms": ["premenstrual dysphoric syndrome","PMDD"],
            "key_criteria": "Marked affective and physical symptoms in the late luteal phase (lability, irritability, dysphoria), remitting after menstruation begins and causing impairment.",
            "duration_threshold": "In most cycles for ≥1 year",
            "typical_onset_age": "Reproductive age",
            "risk_factors": ["hormonal sensitivity", "history of depression/anxiety", "stress"],
            "comorbidity": ["depression", "anxiety", "migraine"],
            "red_flags": ["suicidal ideation in luteal phase"],
            "suicide_risk_level": "Moderate (premenstrual peak)",
            "urgent_referral_criteria": ["recurrent premenstrual suicidal ideation/plan"]
        },
        {
            "id": "ncd_major",
            "disorder": "Major Neurocognitive Disorder (Dementia)",
            "icd10": ["F00.x","F01.x","F02.x","F03"],
            "synonyms": ["dementia","major NCD"],
            "key_criteria": "Significant cognitive decline in ≥1 domain with interference in independence (memory, attention, executive, language, visuospatial).",
            "duration_threshold": "Months–years (progressive)",
            "typical_onset_age": "Older adult (variable by etiology)",
            "risk_factors": ["advanced age", "vascular risk", "APOE ε4", "low education level"],
            "comorbidity": ["depression", "delirium", "anxiety"],
            "red_flags": ["dangerous wandering", "delusional ideas", "domestic risk"],
            "suicide_risk_level": "Low-Moderate (↑ in early stages with insight)",
            "urgent_referral_criteria": ["superimposed delirium", "agitation/aggression with risk"]
        },
        {
            "id": "ncd_mild",
            "disorder": "Mild Neurocognitive Disorder",
            "icd10": ["F06.7"],
            "synonyms": ["mild cognitive impairment","mild NCD"],
            "key_criteria": "Modest decline in ≥1 cognitive domain without loss of independence (greater effort/compensatory strategies).",
            "duration_threshold": "Months–years",
            "typical_onset_age": "Middle–older adult",
            "risk_factors": ["age", "vascular risk", "depression", "low exercise"],
            "comorbidity": ["depression (pseudodementia)", "anxiety"],
            "red_flags": ["rapid decline", "psychotic/focal neurological symptoms"],
            "suicide_risk_level": "Low",
            "urgent_referral_criteria": ["suspicion of delirium", 
            "acute neurological deficits"]
        },
        {
            "id": "delirium",
            "disorder": "Delirium (acute confusional state)",
            "icd10": ["F05"],
            "synonyms": ["acute confusional state","delirium (non-psychotic)"],
            "key_criteria": "Acute and fluctuating onset of disturbance in attention and awareness with cognitive deficits; underlying medical/pharmacological cause.",
            "duration_threshold": "Hours–days",
            "typical_onset_age": "Any age (↑ in older/hospitalized patients)",
            "risk_factors": ["infections", "polypharmacy", "intoxication/withdrawal", "prior dementia"],
            "comorbidity": ["major NCD", "acute medical illnesses"],
            "red_flags": ["severe agitation/hypoactivity", "dehydration", "falls"],
            "suicide_risk_level": "Low (↑ accidental risk)",
            "urgent_referral_criteria": ["immediate medical evaluation", "potentially lethal cause"]
        },
        {
            "id": "circadian_rhythm",
            "disorder": "Circadian Rhythm Sleep-Wake Disorder",
            "icd10": ["G47.2"],
            "synonyms": ["phase shift", "shift work", "circadian desynchronization"],
            "key_criteria": "Chronic misalignment between circadian rhythm and social/work schedules causing insomnia or daytime sleepiness with impairment.",
            "duration_threshold": "≥3 months",
            "typical_onset_age": "Adolescents (delayed phase) or adults (shift/night work)",
            "risk_factors": ["shift work", "nighttime light exposure", "irregular schedules"],
            "comorbidity": ["depression", "anxiety", "insomnia"],
            "red_flags": ["drowsy driving", "dangerous work errors"],
            "suicide_risk_level": "Low-Moderate (via depression/insomnia)",
            "urgent_referral_criteria": ["risk of serious accidents", "associated major depression"]
        },
        {
            "id": "nightmares",
            "disorder": "Nightmare Disorder",
            "icd10": ["F51.5"],
            "synonyms": ["recurrent nightmares","dysphoric dreams"],
            "key_criteria": "Recurrent dysphoric dreams with awakenings and vivid recall; cause distress/insomnia and functional impairment.",
            "duration_threshold": "Recurrent ≥1 month or clinically significant",
            "typical_onset_age": "Childhood (can persist in adults)",
            "risk_factors": ["stress/anxiety", "PTSD", "drugs (e.g., SSRIs, beta-blockers)"],
            "comorbidity": ["PTSD", "anxiety", "depression", "insomnia"],
            "red_flags": ["severe insomnia", "extreme avoidance of sleep"],
            "suicide_risk_level": "Low-Moderate (through depression/insomnia)",
            "urgent_referral_criteria": ["if coexisting suicidal ideation or severe PTSD"]
        },
        {
            "id": "trichotillomania",
            "disorder": "Trichotillomania (Hair-Pulling Disorder)",
            "icd10": ["F63.3"],
            "synonyms": ["hair-pulling"],
            "key_criteria": "Recurrent pulling out of one's hair with visible loss and repeated attempts to decrease or stop; distress/impairment.",
            "duration_threshold": "Chronic/episodic",
            "typical_onset_age": "Late childhood–adolescence",
            "risk_factors": ["stress", "tension before the act", "compulsive-impulsive traits"],
            "comorbidity": ["OCD", "anxiety", "depression"],
            "red_flags": ["trichophagia (risk of trichobezoar)", "skin infections"],
            "suicide_risk_level": "Low-Moderate (↑ if depressed)",
            "urgent_referral_criteria": ["abdominal pain/vomiting from trichobezoar", "associated suicidal ideation"]
        },
        {
            "id": "excoriation",
            "disorder": "Excoriation (Skin-Picking) Disorder",
            "icd10": ["F63.8"],
            "synonyms": ["dermatillomania","skin-picking"],
            "key_criteria": "Recurrent skin picking resulting in lesions, with failed attempts to stop; distress/impairment.",
            "duration_threshold": "Chronic/episodic",
            "typical_onset_age": "Adolescence",
            "risk_factors": ["anxiety/tension", "perfectionism", "stress"],
            "comorbidity": ["OCD", "depression", "anxiety"],
            "red_flags": ["extensive infections/scars", "severe social isolation"],
            "suicide_risk_level": "Low-Moderate (↑ if depressed)",
            "urgent_referral_criteria": ["cellulitis/abscesses", "suicidal ideation due to bodily disfigurement"]
        },
        {
            "id": "psych_factors_medical",
            "disorder": "Psychological Factors Affecting Other Medical Conditions",
            "icd10": ["F54"],
            "synonyms": ["psychological factors in medical illness","pain with psychological factors"],
            "key_criteria": "Psychological/behavioral factors worsen the course of a medical condition, interfere with treatment, or increase risks (e.g., poor adherence, increased pain).",
            "duration_threshold": "Variable (associated with the illness)",
            "typical_onset_age": "Any age",
            "risk_factors": 
            ["chronic illness", "sustained stress", "poor support network"],
            "comorbidity": ["anxiety", "depression", "somatic disorder"],
            "red_flags": ["life-threatening non-adherence (insulin, anticoagulants)", "problematic use of analgesics"],
            "suicide_risk_level": "Moderate (↑ in chronic pain and depression)",
            "urgent_referral_criteria": ["life risk due to non-adherence", "suicidal ideation/plan due to refractory pain"]
        },
        {
            "id": "agoraphobia",
            "disorder": "Agoraphobia",
            "icd10": ["F40.0"],
            "synonyms": ["fear of open spaces","fear of being trapped","avoidance of crowds/transport"],
            "key_criteria": "Fear/avoidance of ≥2 situations (public transport, open/enclosed spaces, lines/crowds, outside home alone) for fear of not being able to escape or get help if panic-like symptoms appear.",
            "duration_threshold": "≥6 months",
            "typical_onset_age": "Late adolescence–early adulthood",
            "risk_factors": ["prior panic", "trait anxiety", "traumatic experiences in public spaces"],
            "comorbidity": ["panic disorder", "GAD", "depression"],
            "red_flags": ["home confinement", "school/work dropout"],
            "suicide_risk_level": "Moderate (↑ if panic/depression)",
            "urgent_referral_criteria": ["suicidal ideation due to severe confinement/isolation"]
        },
        {
            "id": "illness_anxiety",
            "disorder": "Illness Anxiety Disorder",
            "icd10": ["F45.2"],
            "synonyms": ["hypochondriasis","health worry"],
            "key_criteria": "Disproportionate worry about having a serious illness despite adequate medical evaluation; high health anxiety and checking/avoidance behaviors.",
            "duration_threshold": "≥6 months",
            "typical_onset_age": "Young adult–middle age",
            "risk_factors": ["family history of serious illness", "trait anxiety", "previous negative medical experiences"],
            "comorbidity": ["GAD", "OCD", "depression"],
            "red_flags": ["excessive use of medical services", "dangerous avoidance of necessary care"],
            "suicide_risk_level": "Low-Moderate (↑ with depression)",
            "urgent_referral_criteria": ["suicidal ideation due to somatic hopelessness"]
        },
        {
            "id": "hoarding",
            "disorder": "Hoarding Disorder",
            "icd10": ["F42.8"],
            "synonyms": ["compulsive hoarding","hoarding"],
            "key_criteria": "Persistent difficulty discarding possessions due to a perceived need to save them; congestion of living space and impairment.",
            "duration_threshold": "Chronic",
            "typical_onset_age": "Adolescence (worsens in adulthood)",
            "risk_factors": ["family history", "loss events", "insecure attachment styles"],
            "comorbidity": ["OCD", "depression", "ADHD"],
            "red_flags": ["sanitary/fire risk", "self-neglect"],
            "suicide_risk_level": "Low-Moderate (↑ with depression/isolation)",
            "urgent_referral_criteria": ["dangerous living conditions", "inability for self-care"]
        },
        {
            "id": "body_dysmorphic",
            "disorder": "Body Dysmorphic Disorder",
            "icd10": ["F45.2"],
            "synonyms": ["dysmorphophobia","worry about a bodily defect"],
            "key_criteria": "Preoccupation with perceived defects in appearance (not observable or slight) with repetitive behaviors (mirror checking, camouflaging) and distress/impairment.",
            "duration_threshold": "Chronic/episodic",
            "typical_onset_age": "Adolescence",
            "risk_factors": ["perfectionism", "bullying about appearance", 
            "obsessive-compulsive traits"],
            "comorbidity": ["depression", "OCD", "Eating Disorders"],
            "red_flags": ["repeated surgical quests", "severe isolation", "suicidal ideation due to self-image"],
            "suicide_risk_level": "High (especially with depression/Eating Disorders)",
            "urgent_referral_criteria": ["suicidal ideation/plan", "severe food restriction"]
        },
        {
            "id": "bipolar_II",
            "disorder": "Bipolar II Disorder",
            "icd10": ["F31.8"],
            "synonyms": ["bipolar type II","hypomania with major depression"],
            "key_criteria": "≥1 hypomanic episode and ≥1 major depressive episode; never full mania.",
            "duration_threshold": "Recurrent episodes",
            "typical_onset_age": "Adolescence–young adult",
            "risk_factors": ["bipolar family history", "early onset of depression", "rapid cycling"],
            "comorbidity": ["anxiety", "SUD", "BPD"],
            "red_flags": ["depression with suicidal ideation", "risk-taking behaviors in hypomania"],
            "suicide_risk_level": "Very high (similar to bipolar I)",
            "urgent_referral_criteria": ["suicidal ideation/plan", "severe mixed symptoms"]
        },
        {
            "id": "cyclothymia",
            "disorder": "Cyclothymic Disorder",
            "icd10": ["F34.0"],
            "synonyms": ["cyclothymia","chronic mood instability"],
            "key_criteria": "Multiple periods of sub-threshold hypomanic and depressive symptoms, with mood instability.",
            "duration_threshold": "≥2 years (≥1 year in children/adolescents)",
            "typical_onset_age": "Adolescence–young adult",
            "risk_factors": ["family members with mood disorders", "cyclothymic temperament"],
            "comorbidity": ["ADHD", "anxiety", "SUD"],
            "red_flags": ["functional impairment due to lability", "suicidal ideation in low phases"],
            "suicide_risk_level": "Moderate",
            "urgent_referral_criteria": ["active ideation", "substance use with mood dyscontrol"]
        },
        {
            "id": "intermittent_explosive",
            "disorder": "Intermittent Explosive Disorder",
            "icd10": ["F63.81","F63.8"],
            "synonyms": ["anger outbursts","loss of impulse control"],
            "key_criteria": "Recurrent episodes of failure to control aggressive impulses (verbal/physical) disproportionate to the stressor; distress or impairment.",
            "duration_threshold": "≥3 months (frequent) or ≥3 severe episodes in 12 months",
            "typical_onset_age": "Late adolescence–early adulthood",
            "risk_factors": ["exposure to violence", "childhood trauma", "trait impulsivity"],
            "comorbidity": ["ADHD", "SUD", "borderline/antisocial PD"],
            "red_flags": ["injuries to others", "use of weapons", "legal problems"],
            "suicide_risk_level": "Moderate (impulsivity/subsequent guilt)",
            "urgent_referral_criteria": ["imminent risk of harm", "suicidal ideation after episodes"]
        },
        {
            "id": "gambling",
            "disorder": "Gambling Disorder (Pathological Gambling)",
            "icd10": ["F63.0"],
            "synonyms": ["pathological gambling","gambling addiction"],
            "key_criteria": "Persistent and problematic gambling behavior that impairs personal/social/work life: tolerance, chasing losses, lying, financial risk.",
            "duration_threshold": "≥12 months (threshold adjustable by severity)",
            "typical_onset_age": "Early adulthood (sometimes adolescence)",
            "risk_factors": ["easy access to gambling", "depression/anxiety", "impulsivity"],
            "comorbidity": ["depression", "SUD", "borderline PD"],
            "red_flags": ["severe debt", "illegal behaviors", "suicidal ideation due to losses"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["suicide risk", "risk of violence/fraud to finance gambling"]
        },
        {
            "id": "factitious_self",
            "disorder": "Factitious Disorder Imposed on Self",
            "icd10": ["F68.1"],
            "synonyms": ["Munchausen syndrome","malingering is not the same"],
            "key_criteria": "Falsification/induction of physical or psychological signs/symptoms, presenting as ill, without clear external incentives.",
            "duration_threshold": "Variable/episodic",
            "typical_onset_age": "Adulthood",
            "risk_factors": ["history of hospitalizations", 
            "experiences of care/abandonment", "borderline traits"],
            "comorbidity": ["borderline PD", "depression", "SUD"],
            "red_flags": ["self-harm to generate symptoms", "dangerous use of drugs"],
            "suicide_risk_level": "Moderate-High (self-harm/medication)",
            "urgent_referral_criteria": ["acute medical risk", "suspicion of harm to others (if imposed on another)"]
        },
        {
            "id": "substance_induced_psychosis",
            "disorder": "Substance/Medication-Induced Psychotic Disorder",
            "icd10": ["F1x.5"],
            "synonyms": ["substance-induced psychosis","induced psychosis"],
            "key_criteria": "Delusions/hallucinations during or shortly after intoxication/withdrawal/use of drugs with psychotic potential; not better explained by a primary psychosis.",
            "duration_threshold": "Hours–weeks (depending on substance)",
            "typical_onset_age": "Any age (peak in young people)",
            "risk_factors": ["use of cannabis/stimulants/hallucinogens", "psychotic vulnerability", "sleep deprivation"],
            "comorbidity": ["SUD", "anxiety", "depression"],
            "red_flags": ["command hallucinations", "severe agitation", "dangerous behavior"],
            "suicide_risk_level": "High",
            "urgent_referral_criteria": ["psychosis/agitation with risk", "polysubstance use", "hyperthermia/dehydration"]
        },
        {
            "id": "hypothyroidism",
            "disorder": "Hypothyroidism (medical differential for mood/anxiety)",
            "icd10": ["E03.x"],
            "synonyms": ["low thyroid","high TSH"],
            "key_criteria": "Fatigue, hypersomnia, weight gain, dry skin, bradycardia, depressed mood, and cognitive slowing.",
            "duration_threshold": "Weeks–months",
            "typical_onset_age": "Adults (women > men)",
            "risk_factors": ["autoimmune thyroiditis", "postpartum", "thyroid surgery/ablation"],
            "comorbidity": ["depression", "anxiety (secondary)", "hyperlipidemia"],
            "red_flags": ["extreme somnolence", "marked bradycardia", "myxedema"],
            "suicide_risk_level": "Low-Moderate (via secondary depression)",
            "urgent_referral_criteria": ["signs of myxedema (hypothermia, confusion)", "very high TSH with systemic compromise"]
        },
        {
            "id": "hyperthyroidism",
            "disorder": "Hyperthyroidism (medical differential for panic/insomnia)",
            "icd10": ["E05.x"],
            "synonyms": ["high thyroid","suppressed TSH"],
            "key_criteria": "Weight loss, tachycardia, heat intolerance, fine tremor, insomnia, panic-like anxiety/irritability.",
            "duration_threshold": "Weeks–months",
            "typical_onset_age": "Adults (more frequent in women)",
            "risk_factors": ["Graves' disease", "excess levothyroxine"],
            "comorbidity": ["arrhythmias", "osteopenia"],
            "red_flags": ["tachyarrhythmia", "thyroid storm (fever, agitation, confusion)"],
            "suicide_risk_level": "Low-Moderate (due to severe anxiety/insomnia)",
            "urgent_referral_criteria": ["symptoms of severe thyrotoxicosis", "tachycardia >120 with dyspnea/chest pain"]
        },
        {
            "id": "sleep_apnea",
            "disorder": "Obstructive Sleep Apnea (differential for depression/ADHD)",
            "icd10": ["G47.3"],
            "synonyms": ["OSA","snoring with pauses","daytime sleepiness"],
            "key_criteria": "Loud snoring, nighttime breathing pauses, awakenings, morning headache, sleepiness, and mental fog (resembles depression or ADHD).",
            "duration_threshold": "Chronic",
            "typical_onset_age": "Adults (also children with adenotonsillar hypertrophy)",
            "risk_factors": ["obesity", "wide neck", "alcohol/sedative use"],
            "comorbidity": ["hypertension", "depression", "insomnia"],
            "red_flags": ["drowsy driving", "microsleeps in high-risk jobs"],
            "suicide_risk_level": "Low-Moderate (via depression/insomnia)",
            "urgent_referral_criteria": ["high risk of accidents due to sleepiness", "suspicion of severe apnea"]
        },
        {
            "id": "epilepsy",
            "disorder": "Epilepsy (differential for non-epileptic/anxiety seizures)",
            "icd10": ["G40.x"],
            "synonyms": ["convulsions","epileptic seizures"],
            "key_criteria": "Paroxysmal episodes with altered consciousness, tonic-clonic movements, or other ictal phenomena; postictal period with confusion/headache.",
            "duration_threshold": "Recurrent",
            "typical_onset_age": "Bimodal (childhood and >60 years)",
            "risk_factors": ["TBI", "malformations", "tumors", "CNS infections"],
            "comorbidity": ["anxiety", "depression", "postictal psychosis"],
            "red_flags": ["status epilepticus", "trauma from falls", "focal neurological deficit"],
            "suicide_risk_level": "Moderate (↑ if comorbid depression)",
            "urgent_referral_criteria": ["seizure >5 min", "series without recovery", "first seizure episode"]
        },
        {
            "id": "iron_deficiency_anemia",
            "disorder": "Iron Deficiency Anemia (differential for fatigue/depression)",
            "icd10": ["D50.x"],
            "synonyms": ["iron deficiency","low Hb"],
            "key_criteria": "Fatigue, pallor, exertional dyspnea, dizziness; irritability/weakness that can mimic depression.",
            "duration_threshold": "Weeks–months",
            "typical_onset_age": "Any age (prevalent in women of childbearing age)",
            "risk_factors": ["chronic bleeding", "deficient diet", "pregnancy"],
            "comorbidity": ["menstrual disorders", "GI disease"],
            "red_flags": ["active hemorrhage", "very low Hb with syncope"],
            "suicide_risk_level": "Low",
            "urgent_referral_criteria": ["critically low Hb", "signs of shock/hemorrhage"]
        },
        {
            "id": "b12_deficiency",
            "disorder": "Vitamin B12 Deficiency (differential for depression/mild psychosis)",
            "icd10": ["D51.x"],
            "synonyms": ["pernicious anemia","B12 deficit"],
            "key_criteria": "Fatigue, glossitis, paresthesias, ataxia, cognitive and mood alterations (depression/irritability).",
            "duration_threshold": "Months",
            "typical_onset_age": "Older adults, vegans without supplementation",
            "risk_factors": ["malabsorption", "vegan diet", "prolonged metformin use"],
            "comorbidity": ["anemia", "peripheral neuropathy"],
            "red_flags": ["ataxia/neurological progression", "acute confusion"],
            "suicide_risk_level": "Low-Moderate (via depression)",
            "urgent_referral_criteria": ["progressive neurological deficit", "delirium in the elderly"]
        },
        {
            "id": "glycemia_alterations",
            "disorder": "Blood Glucose Alterations (hypo/hyperglycemia) – differential for anxiety/confusion",
            "icd10": ["E10.x","E11.x","E16.2"],
            "synonyms": ["hypoglycemia","hyperglycemia","decompensated diabetes"],
            "key_criteria": "Hypoglycemia: sweating, tremor, anxiety, confusion; Hyperglycemia: polyuria, polydipsia, fatigue, mental fog.",
            "duration_threshold": "Minutes–days (depending on the condition)",
            "typical_onset_age": "Any age (diabetes)",
            "risk_factors": ["diabetes", "irregular diet", "alcohol", "hypoglycemic drugs"],
            "comorbidity": ["depression (in DM)", "anxiety"],
            "red_flags": ["hypoglycemia with loss of consciousness", "ketoacidosis (nausea, abdominal pain, Kussmaul breathing)"],
            "suicide_risk_level": "Low (but high medical risk)",
            "urgent_referral_criteria": ["severe hypoglycemia", "signs of ketoacidosis or hyperosmolarity"]
        },
        {
            "id": "tbi_postconcussive",
            "disorder": "Post-Concussive Syndrome / TBI Sequelae (differential for anxiety/irritability)",
            "icd10": ["F07.2","S06.x"],
            "synonyms": ["post-concussion","post-TBI"],
            "key_criteria": "Headache, dizziness, irritability, emotional lability, difficulty concentrating/memory after TBI.",
            "duration_threshold": "Weeks–months",
            "typical_onset_age": "Any age (post-trauma)",
            "risk_factors": ["previous TBI", "pre-existing anxiety/depression"],
            "comorbidity": ["anxiety", "depression", "insomnia"],
            "red_flags": ["worsening neurological status", "focal deficit", "post-TBI seizures"],
            "suicide_risk_level": "Moderate (chronic pain, personality changes)",
            "urgent_referral_criteria": ["signs of increased intracranial pressure", "syncope/recurrent seizures"]
        },
        {
            "id": "drug_induced_mood",
            "disorder": "Medication-Induced Mood/Anxiety Symptoms",
            "icd10": ["F06.3","T43.x","T38.x (by agent)"],
            "synonyms": ["emotional side effect","psychiatric iatrogenesis"],
            "key_criteria": "Temporal onset after drugs: corticosteroids (euphoria/depression/psychosis), interferon (depression), isotretinoin (mood), stimulants/decongestants/caffeine (anxiety/insomnia).",
            "duration_threshold": "Days–weeks after starting/changing dose",
            "typical_onset_age": "Any age",
            "risk_factors": ["polypharmacy", "high doses", "psychiatric vulnerability"],
            "comorbidity": ["anxiety", "depression"],
            "red_flags": ["steroid psychosis", "suicidal ideation after starting a medication"],
            "suicide_risk_level": "Moderate-High (depending on drug and vulnerability)",
            "urgent_referral_criteria": ["new-onset psychosis/suicidal ideation", "severe symptoms after dose change"]
        },
        {
            "id": "caffeine_pseudoephedrine",
            "disorder": "Caffeine / Pseudoephedrine Stimulation (mimics panic/insomnia)",
            "icd10": ["F15.90","T43.6"],
            "synonyms": ["caffeine intoxication","use of decongestants"],
            "key_criteria": "Nervousness, tremor, palpitations, insomnia, restlessness, and anxiety after high consumption of caffeine/over-the-counter stimulants.",
            "duration_threshold": "Hours–days",
            "typical_onset_age": "Any age",
            "risk_factors": ["high doses", "individual sensitivity", "interactions (SSRIs, theophylline)"],
            "comorbidity": ["anxiety", "insomnia"],
            "red_flags": ["sustained tachycardia", "symptomatic hypertension", "severe agitation"],
            "suicide_risk_level": "Low",
            "urgent_referral_criteria": ["tachyarrhythmias", "severe cardiovascular symptoms"]
        }

    ]
    
    # Datos de screenings
    screenings = [
        {
            "id": 
            "scr_major_dep",
            "objective": "Major Depressive Disorder",
            "synonyms": ["major depression","depressive episode"],
            "screening_questions": [
                "In the last 2 weeks, have you felt sad, empty, or hopeless almost every day?",
                "Have you lost interest or pleasure in activities you used to enjoy?",
                "Have you had trouble with sleep or appetite almost daily?",
                "Have you felt tired, guilty, or had difficulty concentrating?",
                "Have you had thoughts of death or harming yourself?"
            ],
            "positive_indicators": ["≥2 positive core questions (depressed mood/anhedonia)", "≥5 symptoms in 2 weeks with impairment"],
            "key_differentials": ["prolonged grief", "hypothyroidism", "bipolar disorder (depressive episode)", "substance use"],
            "suicide_risk_note": "Increases if there is active ideation, a plan, or previous attempts",
            "escalation": ["Immediate referral if there is active ideation with a plan/means", "Prioritize safety and local emergency contact"]
        },
        {
            "id": "scr_gad",
            "objective": "Generalized Anxiety Disorder",
            "synonyms": ["GAD","excessive worry"],
            "screening_questions": [
                "In the last 6 months, have you worried excessively about various things most days?",
                "Do you find it difficult to control these worries?",
                "Do you have muscle tension, restlessness, irritability, or difficulty sleeping because of this worry?",
                "Do these worries affect your work, studies, or family life?"
            ],
            "positive_indicators": ["Excessive worry that is difficult to control", "≥3 physical symptoms/insomnia", "Functional impairment"],
            "key_differentials": ["hyperthyroidism", "illness anxiety", "panic", "caffeine/stimulant use"],
            "suicide_risk_note": "Moderate risk if depression coexists",
            "escalation": ["If suicidal ideation is present, escalate as depression", "Consider basic medical exclusion (thyroid, substances)"]
        },
        {
            "id": "scr_panic",
            "objective": "Panic Disorder",
            "synonyms": ["panic attacks","panic crisis"],
            "screening_questions": [
                "Have you had sudden attacks of very intense fear with palpitations, shortness of breath, or trembling that peak within minutes?",
                "Are you very worried about having another attack or its consequences (e.g., fainting, losing control)?",
                "Have you changed your behavior to avoid situations for fear of attacks?"
            ],
            "positive_indicators": ["Recurrent unexpected attacks", "Persistent concern and/or behavioral changes for ≥1 month"],
            "key_differentials": ["hyperthyroidism", "heart disease/arrhythmia", "stimulant use", "social anxiety/agoraphobia"],
            "suicide_risk_note": "Moderate-high risk if there is associated hopelessness",
            "escalation": ["Rule out acute medical symptom if chest pain/syncope", "Refer if suicidal ideation or marked disability"]
        },
        {
            "id": "scr_ptsd",
            "objective": "Post-Traumatic Stress Disorder",
            "synonyms": ["PTSD","post traumatic stress"],
            "screening_questions": 
            [
                "Did you experience or witness a very traumatic event (violence, accident, abuse, disaster)?",
                "Do you have intrusive memories, nightmares, or flashbacks of the event?",
                "Do you avoid places, people, or topics that remind you of it?",
                "Do you feel more irritable, on alert, or easily startled?",
                "Has this been happening for more than a month and affecting your daily life?"
            ],
            "positive_indicators": ["Exposure to trauma + re-experiencing + avoidance + hyperarousal", "Duration >1 month with impairment"],
            "key_differentials": ["prolonged grief", "depression", "generalized anxiety", "substance use"],
            "suicide_risk_note": "Elevated in severe/repeated traumas or comorbid depression",
            "escalation": ["Refer immediately if there is active ideation, severe dissociation, or risk of harm"]
        },
        {
            "id": "scr_bipolar",
            "objective": "Bipolar Disorder (I/II) – mania/hypomania screening",
            "synonyms": ["bipolar","hypomania","mania"],
            "screening_questions": [
                "Have you had periods of several days with an unusually elevated or very irritable mood?",
                "During those periods, did you need much less sleep without feeling tired?",
                "Did you feel overly energetic, talk more than usual, or have very racing thoughts?",
                "Did you engage in risky behaviors (spending sprees, unprotected sex, gambling, reckless investments)?"
            ],
            "positive_indicators": 
            ["≥3 activation symptoms (4 if mood is irritable)", "Duration: ≥4 days (hypomania) or ≥7 days / hospitalization (mania)"],
            "key_differentials": ["ADHD", "stimulant use", "cyclothymia", "borderline personality disorder"],
            "suicide_risk_note": "Very high (especially in depressive or mixed phases)",
            "escalation": ["Urgent referral if psychosis, severe agitation, or suicidal/homicidal risk"]
        },
        {
            "id": "scr_psychosis",
            "objective": "Psychotic Spectrum (schizophrenia/brief psychosis/delusional)",
            "synonyms": ["psychosis","hallucinations","delusions"],
            "screening_questions": [
                "Have you heard voices when no one is there or seen things that others don't see?",
                "Do you believe that other people want to harm you or are watching you without clear evidence?",
                "Do you find it hard to organize your thoughts or does your speech become confusing?",
                "Have you noticed a marked loss of motivation or emotional expression?"
            ],
            "positive_indicators": ["Delusions/hallucinations/disorganized speech", "Functional impairment"],
            "key_differentials": ["substance-induced psychosis", "psychotic depression", "bipolar disorder", "delirium/neurological cause"],
            "suicide_risk_note": "High, especially with command hallucinations",
            "escalation": ["Immediate referral if risk to self/others or commands for self-harm/harm"]
        },
        {
            "id": "scr_suicide",
            "objective": "Suicide / self-harm risk (triage)",
            "synonyms": ["suicidal ideation","self-harm"],
            "screening_questions": [
                "Have you thought that you would be better off dead or wished you wouldn't wake up?",
                "In the last few weeks, have you had thoughts of harming yourself or taking your own life?",
                "Have you thought about how you would do it (plan)? Do you have access to means?",
                "Have you ever tried to harm yourself (especially in the last year)?"
            ],
            "positive_indicators": ["Yes to ideation + plan/means/intent or marked hopelessness"],
            "key_differentials": ["major depression", "bipolar disorder", "PTSD", "SUD", "chronic pain/medical illness"],
            "suicide_risk_note": "Critical level if there is a plan, means, or recent attempt",
            "escalation": ["Immediate referral/emergency care", "Do not leave alone, activate support network and local emergency services"]
        },
        {
            "id": "scr_adhd",
            "objective": "Attention-Deficit/Hyperactivity Disorder (adult/childhood)",
            "synonyms": ["ADHD","inattention","hyperactivity"],
            "screening_questions": [
                "Since childhood, have you had difficulty concentrating or finishing tasks?",
                "Do you often lose things, get easily distracted, or avoid long tasks?",
                "Do you feel restless, talk excessively, or act impulsively?",
                "Do these problems occur in two or more settings (home/school/work) and affect your performance?"
            ],
            "positive_indicators": ["Onset before age 12", "Persistent and multi-context pattern", "Current functional impairment"],
            "key_differentials": ["anxiety/depression", "sleep apnea", "medication effects", "hyperthyroidism"],
            "suicide_risk_note": "Low-moderate; increases with depression/SUD",
            "escalation": ["Refer if severe comorbidity or self-harm risk"]
        },
        {
            "id": "scr_social_anxiety",
            "objective": "Social Anxiety Disorder",
            "synonyms": ["social phobia","fear of evaluation"],
            "screening_questions": [
                "Do you feel intense fear of being judged or humiliated in social situations (public speaking, eating in front of others)?",
                "Do you avoid these situations or endure them with great distress?",
                "Does this affect you in your studies, work, or relationships?"
            ],
            "positive_indicators": ["Persistent fear of social evaluation", "Significant avoidance or distress", "Duration ≥6 months"],
            "key_differentials": ["selective mutism", "agoraphobia", "avoidant personality disorder"],
            
            "suicide_risk_note": "Moderate if there is isolation and depression",
            "escalation": ["Refer if extreme isolation or suicidal ideation"]
        },
        {
            "id": "scr_ocd",
            "objective": "Obsessive-Compulsive Disorder",
            "synonyms": ["OCD","obsessions and compulsions"],
            "screening_questions": [
                "Do you have repeated, unwanted thoughts or images that cause you anxiety (e.g., contamination, harm, morality)?",
                "Do you perform repetitive acts (washing, checking, ordering) to reduce that anxiety?",
                "Do they take up more than 1 hour a day or affect your daily life?"
            ],
            "positive_indicators": ["Ego-dystonic obsessions/compulsions", ">1 hour/day or significant impairment"],
            "key_differentials": ["OCPD (traits)", "psychotic spectrum", "dysmorphic disorder", "tics/Tourette's"],
            "suicide_risk_note": "Moderate (↑ if depression/aggressive obsessions)",
            "escalation": ["Refer if self-harm/obsessions with harm or severe functional disability"]
        },
        {
            "id": "scr_insomnia",
            "objective": "Insomnia Disorder",
            "synonyms": ["chronic insomnia","difficulty sleeping"],
            "screening_questions": [
                "Do you have trouble falling or staying asleep, or do you wake up too early at least 3 nights a week?",
                "Has this been happening for 3 months or more?",
                "Does it affect your energy, concentration, or mood during the day?"
            ],
            "positive_indicators": ["Frequency ≥3 nights/week", "Duration ≥3 months", "Daytime impairment"],
            "key_differentials": ["sleep apnea", "depression/anxiety", "caffeine, nicotine, alcohol", "shift work"],
            "suicide_risk_note": "Moderate if coexisting depression/ideation",
            "escalation": ["Refer if suicidal ideation or sleepiness with high risk (driving/machinery)"]
        },
        {
            "id": "scr_alcohol",
            "objective": "Alcohol Use Disorder (brief screening like AUDIT-C)",
            "synonyms": ["alcoholism","problematic alcohol use"],
            
            "screening_questions": [
                "How often do you have a drink containing alcohol?",
                "On a typical day when you are drinking, how many drinks do you have?",
                "How often do you have 4 (for women) / 5 (for men) or more drinks on one occasion?"
            ],
            "positive_indicators": ["High weekly consumption", "Binge drinking episodes", "Work/social problems due to drinking"],
            "key_differentials": ["depression/anxiety (self-medication)", "sleep disorders", "sedative/opioid use"],
            "suicide_risk_note": "High if there is depression/comorbidity or previous attempts",
            "escalation": ["Urgent referral if complicated withdrawal, suicidal ideation, severe intoxication, or violence"]
        },
        {
            "id": "scr_asd",
            "objective": "Autism Spectrum Disorder (pediatric conversational screening)",
            "synonyms": ["ASD","autism"],
            "screening_questions": [
                "Since childhood, have they shown difficulties in social interaction (eye contact, gestures, shared play)?",
                "Do they have very restricted interests or repetitive behaviors (lining up objects, echolalia, rigid routines)?",
                "Are these difficulties observed at home and school and do they limit their adaptation?"
            ],
            "positive_indicators": ["Social deficits + repetitive patterns", "Early onset", "Multi-context"],
            "key_differentials": ["ADHD", "intellectual disability", "social deprivation", "language disorders"],
            "suicide_risk_note": "Moderate in high-functioning ASD with depression",
            "escalation": ["Refer if self-harm/ideation or developmental regression"]
        }
    ]
    
    # Datos de respuestas
    responses = [
        {
            "id": "resp_validation_01",
            "type": "emotional_validation",
            "objective": "Open the conversation with empathy and safety",
            "language": "you",
            "template": [
                "Thank you for sharing this. I'm sorry you're going through such a difficult situation. I'm here to support you and explore options together.",
                "I appreciate your trust. What you're feeling is important and deserves attention. We can move forward step by step."
            ],
            "when_to_use": ["start of conversation", "emotional distress", "shame/hesitation in sharing"],
            "safety_notes": ["avoid minimizing", "do not pass judgment", "do not promise absolute confidentiality in a crisis"]
            },
            {
            "id": "resp_reflection_02",
            "type": "reflective_summary",
            "objective": "Show understanding and organize what has been reported",
            "language": "you",
            "template": [
                "If I understand correctly, in the last few weeks you have had {{key_symptoms}} and this has affected you in {{affected_areas}}. Is that correct?",
                "Let me check: you're noticing {{symptom_1}}, {{symptom_2}}, and {{symptom_3}}, and you are concerned about {{main_concern}}. Can you confirm?"
            ],
            "when_to_use": ["confusion of motives", "several scattered symptoms"],
            "safety_notes": ["use closed questions to confirm", "avoid labeling at this stage"]
            },
            {
            "id": "resp_permission_03",
            "type": "asking_permission",
            "objective": "Obtain consent for sensitive screening",
            "language": "you",
            "template": [
                "Is it okay if I ask you a few brief questions to better understand your emotional well-being?",
                "To support you safely, can we quickly review some risk signs?"
            ],
            "when_to_use": ["before risk screeners", "sensitive topics"],
            "safety_notes": ["state duration and purpose", "respect if they do not wish to continue and offer alternatives"]
            },
            {
            "id": "resp_psychoed_04",
            "type": "brief_psychoeducation",
            "objective": "Normalize and explain without diagnosing",
            "language": "you",
            "template": [
                "Some people with symptoms like {{core_symptom}} also experience {{associated_symptom}}. This doesn't mean a diagnosis, but it does mean it's worth evaluating with a professional.",
                "Changes in sleep, appetite, or energy can be related to emotional state or medical conditions. We can explore both fronts."
            ],
            "when_to_use": ["after initial screening", "doubts about symptoms"],
            "safety_notes": ["avoid labels", "invite clinical evaluation"]
            },
            {
            "id": "resp_suicide_check_05",
            "type": "suicide_risk_check",
            "objective": "Explore safety directly and compassionately",
            "language": "you",
            "template": [
                "I want to make sure you're safe: have you had thoughts of harming yourself or that life is not worth living?",
                "Have you thought about how you would do it or do you have access to means to harm yourself?"
            ],
            "when_to_use": ["severe depressive symptoms", "hopelessness", "recent loss", "mention of death"],
            "safety_notes": ["if ideation/plan/means → activate emergency protocol", "maintain a calm and concrete tone"]
            },
            {
            "id": "resp_psychosis_check_06",
            "type": "psychosis_risk_check",
            "objective": "Detect symptoms of psychosis and commands",
            "language": "you",
            "template": [
                "Have you heard voices or seen things that other people don't perceive?",
                "Does any voice or idea tell you to harm yourself or others?"
            ],
            "when_to_use": ["disorganized behavior", "suspicion of psychosis", "substance use", "postpartum"],
            "safety_notes": ["if 'commands' or risk → urgent referral", "do not confront beliefs, validate for safety"]
            },
            {
            "id": "resp_mania_check_07",
            "type": "mania_risk_check",
            "objective": "Detect dangerous activation",
            "language": "you",
            "template": [
                "These days, are you sleeping much less without feeling tired?",
                "Have you made impulsive decisions that could cause you problems (spending, gambling, driving fast)?"
            ],
            "when_to_use": ["euphoria/irritability + little sleep", "history of bipolar disorder"],
            "safety_notes": ["if high-risk behaviors → urgent referral"]
            },
            {
            "id": "resp_violence_abuse_08",
            "type": "violence_abuse_check",
            "objective": "Explore domestic safety with sensitivity",
            "language": "you",
            "template": [
                "For your safety: has anyone recently physically hurt you, sexually forced you, or threatened you?",
                "If you don't want to answer now, that's okay. We can review resources when you feel ready."
            ],
            "when_to_use": ["unexplained injuries", "fear of home/partner", "coercive control"],
            "safety_notes": ["if imminent risk → emergency; prioritize local resources", "avoid endangering the user"]
            },
            {
            "id": "resp_emergency_09",
            "type": "immediate_emergency_protocol",
            "objective": "Clear instructions in case of imminent risk",
            "language": "you",
            "template": [
                "Your safety is the priority. If the risk is immediate, please contact emergencies at {{local_emergency_number}} or go to the nearest emergency room.",
                "If possible, ask someone you trust to accompany you right now. I can stay with you in this chat while you make the call."
            ],
            "when_to_use": ["ideation with plan/means", "command hallucinations", "recent attempt", "ongoing violence"],
            "urgent_referral_criteria": ["plan + means", "psychosis with commands", "severe intoxication/withdrawal", "postpartum with psychosis"],
            "safety_notes": ["do not end the conversation abruptly", "prioritize short instructions and action"]
            },
            {
            "id": "resp_safety_plan_10",
            "type": "brief_safety_plan",
            "objective": "Co-create immediate protective measures",
            "language": "you",
            "template": [
                "Let's build a brief plan: 1) Remove or limit access to {{means_of_risk}}; 2) Contact {{trusted_person}}; 3) Identify a safe place ({{safe_place}}); 4) Call {{local_emergency_number}} if the risk increases.",
                "Does it seem okay to write down these steps and keep them visible today?"
            ],
            "when_to_use": ["high but not imminent risk", "waiting for transfer to resources"],
            "safety_notes": ["check for understanding", "offer to re-check in minutes if still in chat"]
            },
            {
            "id": "resp_referral_11",
            "type": "referral_guidance",
            "objective": "Guide to professional care without imposing",
            "language": "you",
            "template": [
                "For adequate support, a clinical evaluation with a psychologist or doctor is recommended. I can suggest looking for resources at {{local_resource}} or your nearest health center.",
                "Would you like me to share key questions for your appointment (symptoms, duration, impact, comorbidities)?"
            ],
            "when_to_use": ["moderate to severe symptoms", "persistence >2-4 weeks", "medical comorbidity"],
            "safety_notes": ["do not delay referral in case of risk", "respect cultural and access preferences"]
            },
            {
            "id": "resp_coping_12",
            "type": "short_term_techniques",
            "objective": "Immediate regulation strategies (not a substitute for therapy)",
            "language": "you",
            "template": [
                "We can try a brief technique now: 4-4-6 breathing for 3 minutes (inhale 4, hold 4, exhale 6). Sound good?",
                "Another quick option is 'sensory anchoring': name 5 things you see, 4 you feel, 3 you hear, 2 you smell, and 1 you taste."
            ],
            "when_to_use": ["acute anxiety", "initial insomnia", "rumination"],
            "safety_notes": ["explain it's temporary relief", "if it worsens → refer"]
            },
            {
            "id": "resp_sleep_hygiene_13",
            "type": "sleep_psychoeducation",
            "objective": "Basic safe sleep guidelines",
            "language": "you",
            "template": [
                "Try regular schedules, avoid caffeine 6–8 hours before bed, and screens 60 minutes before. If you don't fall asleep in 20–30 minutes, get up and do something quiet until you feel sleepy.",
                "If you snore loudly or have breathing pauses, it's a good idea to get it checked (it could impact mood and attention)."
            ],
            "when_to_use": ["insomnia", "daytime fatigue"],
            "safety_notes": ["if drowsy while driving → avoid driving and refer"]
            },
            {
            "id": "resp_limits_14",
            "type": "no_diagnosis_disclaimer",
            "objective": "Establish the agent's clinical limits",
            "language": "you",
            "template": [
                "I can guide you with information and supportive questions, but I cannot issue a diagnosis or replace a clinical consultation. My goal is to help you approach your healthcare professional with more clarity.",
                "Let's work on identifying signs and nearby support options."
            ],
            "when_to_use": ["when asked for diagnosis or medication", "before closing a complex case"],
            "safety_notes": ["refer if severe", "avoid pharmacological recommendations"]
            },
            {
            "id": "resp_closure_15",
            "type": "closure_with_reframing",
            "objective": "Close while maintaining support and next steps",
            "language": "you",
            "template": [
                "Thank you for your openness today. To summarize: {{brief_summary}}. Next steps: {{step_1}}, {{step_2}}. If you notice the risk increasing, contact {{local_emergency_number}}.",
                "Would you like us to review how you did with these steps in your next conversation?"
            ],
            "when_to_use": ["end of interaction", "after action plan"],
            "safety_notes": ["reiterate warning signs", "invite follow-up with a professional"]
            }

    ]
    
    # Datos de expresiones coloquiales
    colloquial = [
        {
        "id": "col_nerve_attacks",
        "term": "attacks of nerves",
        "variants": ["an attack is grabbing me","my nerves are getting the best of me","nervous crisis"],
        "possible_intentions": ["Panic Disorder","Agoraphobia","Generalized Anxiety","PTSD"],
        "clues": ["sudden onset","palpitations","shortness of breath","fear of dying/going crazy"],
        "red_flags": ["intense chest pain","fainting","suicidal ideation"],
        "suggested_questions": ["Do the episodes peak within minutes?", "Do you avoid places for fear of another attack?"]
        },
        {
        "id": "col_general_nerves",
        "term": "the nerves",
        "variants": ["I'm nervous","my nerves are eating me up"],
        "possible_intentions": ["Generalized Anxiety","Social Anxiety","Illness Anxiety Disorder"],
        "clues": ["chronic worry","muscle tension","insomnia"],
        "red_flags": ["marked weight loss","sustained tachycardia"],
        "suggested_questions": ["Have you been worrying about many things most days for 6 months or more?"]
        },
        {
        "id": "col_feeling_down",
        "term": "feeling down",
        "variants": ["the blues hit me","I'm feeling sad","I'm drained"],
        "possible_intentions": ["Major Depressive Disorder","Dysthymia"],
        "clues": ["low mood","anhedonia","fatigue","guilt"],
        "red_flags": ["thoughts of death","self-neglect"],
        "suggested_questions": ["Have you been feeling this way almost every day for two weeks or more?"]
        },
        {
        "id": "col_no_desire",
        "term": "I don't feel like doing anything",
        "variants": ["nothing motivates me","I don't enjoy things anymore"],
        "possible_intentions": ["Major Depressive Disorder","Dysthymia"],
        "clues": ["central anhedonia","isolation"],
        "red_flags": ["suicidal ideation","refusal of food"],
        "suggested_questions": ["Have you lost interest in activities you used to enjoy?"]
        },
        {
        "id": "col_bad_thoughts",
        "term": "bad thoughts",
        "variants": ["thoughts of not being here anymore","wanting to disappear"],
        "possible_intentions": ["Suicide Risk","Major Depression","Bipolar (depressive phase)","PTSD"],
        "clues": ["hopelessness","guilt","ideation of death"],
        "red_flags": ["plan/means available","previous attempt"],
        "suggested_questions": ["Have you thought about how you would do it or do you have access to means?"]
        },
        {
        "id": "col_cant_sleep",
        "term": "I can't get a wink of sleep",
        "variants": ["I can't sleep","I sleep in fits and starts"],
        "possible_intentions": ["Insomnia Disorder","Anxiety","Depression","Circadian Rhythm Disorder"],
        "clues": ["prolonged latency","awakenings","daytime fatigue"],
        "red_flags": ["drowsy driving","nocturnal suicidal ideation"],
        "suggested_questions": ["Does this happen ≥3 nights/week for ≥3 months?"]
        },
        {
        "id": "col_nightmares",
        "term": "nightmares",
        "variants": ["bad dreams","waking up scared"],
        "possible_intentions": ["Nightmare Disorder","PTSD","Anxiety"],
        "clues": ["vivid recall","sleep avoidance"],
        "red_flags": ["severe insomnia","suicidal ideation from hopelessness"],
        "suggested_questions": ["Are the nightmares related to a major event?"]
        },
        {
        "id": "col_i_choke",
        "term": "I'm losing my breath",
        "variants": ["I can't breathe","I'm short of breath"],
        "possible_intentions": ["Panic Disorder","Anxiety","Hyperthyroidism (differential)","Cardiopulmonary (differential)"],
        
        "clues": ["sudden onset + fear","paresthesias"],
        "red_flags": ["chest pain","cyanosis","syncope"],
        "suggested_questions": ["Does it happen suddenly and with palpitations/trembling?"]
        },
        {
        "id": "col_hands_shaking",
        "term": "my hands are shaking",
        "variants": ["internal tremor","nervousness"],
        "possible_intentions": ["Anxiety","Hyperthyroidism (differential)","Caffeine/stimulants (differential)"],
        "clues": ["insomnia","palpitations","weight loss"],
        "red_flags": ["tachyarrhythmia","high consumption of caffeine/meds"],
        "suggested_questions": ["Did you increase caffeine or take decongestants?"]
        },
        {
        "id": "col_feel_out_of_place",
        "term": "I feel out of sorts",
        "variants": ["I feel weird","I feel empty"],
        "possible_intentions": ["Depression","Generalized Anxiety","Depersonalization/Derealization"],
        "clues": ["anhedonia or detachment","fatigue"],
        "red_flags": ["suicidal ideation","substance use"],
        "suggested_questions": ["Do you feel disconnected from yourself or your surroundings?"]
        },
        {
        "id": "col_social_shyness",
        "term": "I'm very shy to speak",
        "variants": ["I'm embarrassed by people","I turn red"],
        "possible_intentions": ["Social Anxiety","Selective Mutism (childhood)","Avoidant PD"],
        "clues": ["fear of evaluation","avoidance"],
        "red_flags": ["extreme isolation","school/work dropout"],
        "suggested_questions": ["Do you avoid activities for fear of being judged?"]
        },
        {
        "id": "col_cant_concentrate",
        "term": "I can't concentrate",
        "variants": ["my mind goes blank","I forget things"],
        "possible_intentions": ["Depression","ADHD","Anxiety","Mild NCD (elderly)"],
        "clues": ["persistent distraction","childhood onset (ADHD) or recent (depression)"],
        "red_flags": ["rapid decline in the elderly","work-related risk"],
        "suggested_questions": ["Since childhood, have you had attention problems in more than one place?"]
        },
        {
        "id": "col_arrange_everything",
        "term": "I need to arrange everything",
        "variants": ["I wash my hands all the time","I check things many times"],
        "possible_intentions": ["OCD","OCPD (traits)"],
        "clues": ["ego-dystonic obsessions/compulsions",">1hr/day"],
        "red_flags": ["lesions from washing","ideation from distress"],
        "suggested_questions": ["Do the rituals take up more than an hour of your day?"]
        },
        {
        "id": "col_look_at_myself_much",
        "term": "I see flaws in myself",
        "variants": ["I don't like my face","I check myself all the time"],
        "possible_intentions": ["Body Dysmorphic Disorder","Depression","Eating Disorder"],
        "clues": ["camouflaging/hiding","seeking surgery"],
        "red_flags": ["suicidal ideation due to appearance","food restriction"],
        "suggested_questions": ["Does the worry about your appearance affect your daily life?"]
        },
        {
        "id": "col_dont_eat_well",
        "term": "I don't eat well",
        "variants": ["I skip meals","I make myself vomit"],
        "possible_intentions": ["Eating Disorder (AN/BN/BED)","Depression"],
        "clues": ["weight loss","purging behaviors"],
        "red_flags": ["very low BMI","syncope","electrolyte imbalance"],
        "suggested_questions": ["Have you lost weight quickly or used methods to lose weight?"]
        },
        {
        "id": "col_feeling_revved_up",
        "term": "I'm feeling revved up",
        "variants": ["I can't stop","a thousand ideas","I talk a lot"],
        "possible_intentions": ["Hypomania/Mania (Bipolar)","Stimulants (differential)","Anxiety"],
        "clues": ["little sleep without tiredness","spending/impulsivity"],
        "red_flags": ["high-risk behaviors","agitation with little need for sleep"],
        "suggested_questions": ["Are you sleeping much less and still have too much energy?"]
        },
        {
        "id": "col_amped_up",
        "term": "I'm amped up",
        "variants": ["I'm on a high","feeling a hundred percent"],
        "possible_intentions": ["Stimulant Use","Hypomania/Mania"],
        "clues": 
        ["euphoria + dilated pupils","insomnia"],
        "red_flags": ["psychosis","hyperthermia/dehydration"],
        "suggested_questions": ["Have you consumed anything (powder/pills/energy drinks) recently?"]
        },
        {
        "id": "col_hangover_shakes",
        "term": "hangover shakes",
        "variants": ["the morning after blues","I shake from stopping drinking"],
        "possible_intentions": ["Alcohol Withdrawal","Alcohol Use Disorder"],
        "clues": ["sweating","anxiety","insomnia"],
        "red_flags": ["delirium tremens","seizures"],
        "suggested_questions": ["Is it worse in the mornings and improves when you drink?"]
        },
        {
        "id": "col_smoke_weed",
        "term": "I smoke weed",
        "variants": ["I smoke herb","I'm greening out"],
        "possible_intentions": ["Cannabis Use Disorder","Substance-Induced Psychosis"],
        "clues": ["daily use","apathy","anxiety/paranoia"],
        "red_flags": ["psychotic symptoms","school dropout"],
        "suggested_questions": ["Have you had strange ideas or heard voices when you smoke?"]
        },
        {
        "id": "col_scared_of_people",
        "term": "people scare me",
        "variants": ["I can't handle crowds","I'm panicked about going out"],
        "possible_intentions": ["Agoraphobia","Social Anxiety","Panic"],
        "clues": ["avoids lines/transport","fear of escape"],
        "red_flags": ["home confinement","school/work impairment"],
        "suggested_questions": ["Do you avoid two or more of these: transport, open/closed spaces, lines, going out alone?"]
        },
        {
        "id": "col_hear_voices",
        "term": "I hear voices",
        "variants": ["I hear things","they talk to me"],
        "possible_intentions": ["Schizophrenia Spectrum","Substance-Induced Psychosis","Brief Psychosis"],
        "clues": ["second/third person voices","commands"],
        "red_flags": ["commands to harm","risk to self/others"],
        "suggested_questions": ["Does any voice tell you to harm yourself or someone else?"]
        },
        {
        "id": "col_see_shadows", 
        "term": "I see shadows",
        "variants": ["I see things others don't","shadows following me"],
        "possible_intentions": ["Psychosis","Delirium (differential if acute)","Substances"],
        "clues": ["visual hallucinations","paranoia"],
        "red_flags": ["acute confusion","intoxication"],
        "suggested_questions": ["Did it start suddenly after consuming something or being sick?"]
        },
        {
        "id": "col_detached_from_reality",
        "term": "I feel outside of myself",
        "variants": ["like in a movie","everything feels unreal"],
        "possible_intentions": ["Depersonalization/Derealization","Anxiety/Panic","PTSD"],
        "clues": ["intact reality testing","stress"],
        "red_flags": ["ideation from intense distress"],
        "suggested_questions": ["Do you know this is a feeling and not something that is actually happening?"]
        },
        {
        "id": "col_chest_pain_anxiety",
        "term": "chest pain from nerves",
        "variants": ["my heart is pounding","tachycardia from fright"],
        "possible_intentions": ["Panic","Anxiety","Cardiovascular (differential)"],
        "clues": ["peaks in minutes","fear of dying"],
        "red_flags": ["oppressive pain with effort","radiation","persistent cold sweat"],
        "suggested_questions": ["Does the pain appear with effort or at rest during a fear crisis?"]
        },
        {
        "id": "col_overthinking",
        "term": "I keep overthinking",
        "variants": ["I ruminate a lot","I can't stop turning it over in my mind"],
        "possible_intentions": ["Generalized Anxiety","Depression","OCD (if intrusive)"],
        "clues": ["worry difficult to control","insomnia"],
        "red_flags": ["marked hopelessness"],
        "suggested_questions": ["Do you find it hard to stop the worries even if you try?"]
        },
        {
        "id": "col_forget_everything",
        "term": "I forget everything",
        "variants": ["bad memory","foggy head"],
        "possible_intentions": ["Depression","Mild/Major NCD","Sleep Apnea","Anxiety"],
        
        "clues": ["gradual vs abrupt onset","functionality"],
        "red_flags": ["disorientation","dangerous loss of objects (gas/keys)"],
        "suggested_questions": ["Did it start recently or since you were young? Does it get worse with sleep?"]
        },
        {
        "id": "col_pain_no_cause",
        "term": "everything hurts",
        "variants": ["pains without a cause","everything bothers me"],
        "possible_intentions": ["Somatic Symptom Disorder","Anxiety/Depression","Pain with psychological factors"],
        "clues": ["high health worry","repeated help-seeking"],
        "red_flags": ["weight loss/fever","neurological signs"],
        "suggested_questions": ["How much do these pains affect your daily life?"]
        },
        {
        "id": "col_jealous_ideas",
        "term": "I get it in my head that they're cheating",
        "variants": ["jealousy I can't control","convinced without proof"],
        "possible_intentions": ["Delusional Disorder (jealous type)","Borderline PD (jealousy/abandonment)"],
        "clues": ["fixed conviction","little evidence"],
        "red_flags": ["intimate partner violence","surveillance/threats"],
        "suggested_questions": ["Have you thought about or tried to check up on or follow your partner?"]
        },
        {
        "id": "col_dont_leave_house",
        "term": "I don't leave the house",
        "variants": ["I shut myself in","fear of going out"],
        "possible_intentions": ["Agoraphobia","Major Depression","Social Anxiety"],
        "clues": ["avoidance of ≥2 situations","isolation"],
        "red_flags": ["school/work dropout","suicide risk from isolation"],
        "suggested_questions": ["What places do you avoid and since when?"]
        },
        {
        "id": "col_magical_thinking_bad",
        "term": "I feel like I'm being followed or watched",
        "variants": ["paranoia","they're watching me"],
        "possible_intentions": ["Psychotic Spectrum","Severe Anxiety","Cannabis/stimulants (differential)"],
        "clues": ["ideas of reference","hypervigilance"],
        "red_flags": ["risk of defensive aggression","command hallucinations"],
        "suggested_questions": ["Do you have proof that you are being followed or is it a persistent feeling?"]
        }
    ]
    
    # Crear uploader y cargar datos
    uploader = MentalHealthDataUploader()
    
    data = {
        'disorders': disorders_main,
        'screenings': screenings,
        'responses': responses,
        'colloquial': colloquial
    }
    
    print("=" * 60)
    print("MENTAL HEALTH DATA UPLOAD TO CHROMADB")
    print("=" * 60)
    
    try:
        uploader.upload_all_data(data)
        print("\n" + "=" * 60)
        print("✓ ALL DATA UPLOADED SUCCESSFULLY")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error during upload: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()