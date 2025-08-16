from __future__ import annotations
import re, uuid
from typing import Dict, List
from datetime import datetime

class CVParser:
    def __init__(self):
        self.buzzwords = [
            'blockchain', 'ai', 'artificial intelligence', 'cloud', 'big data', 'iot', 'robotics', 'devops', 'microservices', 'agile', 'scrum', 'digital transformation', 'data mining', 'data engineering', 'data visualization', 'nlp', 'deep learning', 'machine learning', 'crypto', 'web3', 'metaverse', '5g', 'virtual reality', 'augmented reality', 'quantum computing', 'saas', 'paas', 'iaas', 'no code', 'low code', 'growth hacking', 'design thinking', 'lean', 'kanban', 'product management', 'stakeholder management', 'change management', 'business intelligence', 'erp', 'crm', 'rpa', 'automation', 'cybersecurity', 'penetration testing', 'ethical hacking', 'block chain', 'block-chain'
        ]
        self.soft_skill_patterns = [
            r'communication', r'teamwork', r'leadership', r'problem[- ]?solving', r'critical thinking', r'adaptability', r'creativity', r'time management', r'conflict resolution', r'collaboration', r'initiative', r'work ethic', r'flexibility', r'organization', r'presentation', r'negotiation', r'customer service', r'project management', r'coaching', r'mentoring', r'planning', r'analytical', r'fast learner', r'open-minded', r'positive attitude', r'decision making', r'self-motivation', r'active listening', r'empathy', r'interpersonal', r'public speaking', r'goal setting', r'self discipline', r'persuasion', r'networking', r'accountability', r'initiative', r'patience', r'resilience', r'growth mindset'
        ]
        self.skill_synonyms = {
            'javascript': ['js','javascript','node.js','nodejs','react.js','reactjs'],
            'python': ['python','python3','py','django','flask','fastapi'],
            'java': ['java','spring','spring boot','springboot'],
            'php': ['php','laravel','symfony','codeigniter'],
            'c#': ['c#','csharp','c sharp','.net','dotnet','asp.net'],
            'c++': ['c++','cpp','c plus plus'],
            'typescript': ['typescript','ts'],
            'go': ['golang','go'],
            'react': ['react','reactjs','react.js'],
            'vue': ['vue','vuejs','vue.js'],
            'angular': ['angular','angularjs'],
            'html': ['html','html5'],
            'css': ['css','css3','scss','sass','less'],
            'nodejs': ['node.js','nodejs','node'],
            'express': ['express','expressjs'],
            'django': ['django'],
            'flask': ['flask'],
            'fastapi': ['fastapi'],
            'spring': ['spring','spring boot'],
            'mysql': ['mysql'],
            'postgresql': ['postgresql','postgres','psql'],
            'mongodb': ['mongodb','mongo'],
            'redis': ['redis'],
            'elasticsearch': ['elasticsearch','elastic'],
            'sqlite': ['sqlite'],
            'aws': ['aws','amazon web services'],
            'azure': ['azure','microsoft azure'],
            'gcp': ['gcp','google cloud','google cloud platform'],
            'docker': ['docker'],
            'kubernetes': ['kubernetes','k8s'],
            'jenkins': ['jenkins'],
            'git': ['git','github','gitlab'],
            'machine learning': ['ml','machine learning','artificial intelligence','ai'],
            'data science': ['data science','data analysis','data analytics'],
            'ui/ux': ['ui','ux','ui/ux','user interface','user experience'],
            'project management': ['project management','pm','scrum','agile'],
        }
        self.location_synonyms = {
            'hanoi': ['hanoi','ha noi','hn','hà nội'],
            'ho chi minh city': ['ho chi minh city','hcmc','hcm','tp hcm','saigon','sài gòn'],
            'da nang': ['da nang','danang','đà nẵng'],
            'vietnam': ['vietnam','viet nam','việt nam','vn'],
        }

    def extract_contact_info(self, text: str) -> Dict[str, List[str]]:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        emails = re.findall(email_pattern, text, flags=re.IGNORECASE)

        # khá rộng rãi: số có 10-13 ký tự (cho quốc tế/VN)
        phone_pattern = r'(\+?\d[\d\s().-]{8,}\d)'
        raw = re.findall(phone_pattern, text)
        phones = []
        for p in raw:
            digits = re.sub(r'[^\d+]', '', p)
            if len(re.sub(r'\D', '', digits)) >= 10:
                phones.append(digits)

        emails = sorted(set(e.lower() for e in emails))
        phones = sorted(set(phones))
        return {'emails': emails, 'phones': phones}

    def extract_name(self, text: str) -> str:
        # Ignore lines containing 'email' (case-insensitive)
        lines = [ln.strip() for ln in text.splitlines()[:10] if ln.strip() and len(ln.strip()) < 100 and 'email' not in ln.lower()]
        # 1. Prioritize all-uppercase lines (likely name at top of CV)
        for line in lines:
            if (
                re.match(r'^[A-Z\s]+$', line)
                and 2 <= len(line.split()) <= 5
                and len(line) > 5
            ):
                # Merge consecutive single-letter tokens (e.g. 'Ch Au' -> 'Chau')
                tokens = line.split()
                merged = []
                i = 0
                while i < len(tokens):
                    if i < len(tokens) - 1 and len(tokens[i]) == 2 and len(tokens[i+1]) == 2:
                        merged.append(tokens[i] + tokens[i+1])
                        i += 2
                    else:
                        merged.append(tokens[i])
                        i += 1
                return ' '.join(merged)
        # 2. Try common name patterns
        name_patterns = [
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'Name:\s*([A-Za-z\s]+)',
            r'Full Name:\s*([A-Za-z\s]+)',
            r'Họ tên:\s*([A-Za-z\s]+)',
        ]
        for line in lines:
            for pattern in name_patterns:
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    nm = m.group(1).strip()
                    if 2 <= len(nm.split()) <= 5:
                        return nm
        # 3. Fallback: first reasonable line
        for line in lines[:5]:
            if re.match(r'^[A-Za-z\s]+$', line) and 2 <= len(line.split()) <= 5:
                return line
        return "Unknown"

    def extract_skills(self, text: str) -> List[str]:
        t = text.lower()
        tech_found = set()
        buzz_found = set()
        soft_found = set()
        all_found = set()

        # Technical skills from synonyms
        for norm, syns in self.skill_synonyms.items():
            for s in syns:
                if re.search(r'\b' + re.escape(s) + r'\b', t):
                    tech_found.add(norm); break

        # Buzzwords
        for buzz in self.buzzwords:
            if re.search(r'\b' + re.escape(buzz) + r'\b', t):
                buzz_found.add(buzz)

        # Soft skills
        for pat in self.soft_skill_patterns:
            if re.search(r'\b' + pat + r'\b', t):
                soft_found.add(pat.replace('-', ' ').title())

        # Extract all skills from SKILLS blocks
        blocks = re.findall(
            r'(?:skills?|technical skills?|programming languages?|technologies?|soft skills?)[\s:]*([^\n]+(?:\n(?!\n)[^\n]+)*)',
            text, flags=re.IGNORECASE)
        for blk in blocks:
            items = re.findall(r'[A-Za-z][A-Za-z0-9+#.\s-]+', blk)
            for it in items:
                itl = it.strip().lower()
                all_found.add(itl)
                # Classify
                for norm, syns in self.skill_synonyms.items():
                    if itl in [x.lower() for x in syns]:
                        tech_found.add(norm)
                for buzz in self.buzzwords:
                    if buzz == itl:
                        buzz_found.add(buzz)
                for pat in self.soft_skill_patterns:
                    if pat.replace('-', ' ') == itl:
                        soft_found.add(pat.replace('-', ' ').title())

        # Remove duplicates
        tech_skills = sorted(tech_found)
        buzz_skills = sorted(buzz_found)
        soft_skills = sorted(soft_found)
        all_skills = sorted(all_found)
        return {
            'technical_skills': tech_skills,
            'soft_skills': soft_skills,
            'buzzwords': buzz_skills,
            'all_skills': all_skills
        }

    def extract_locations(self, text: str) -> List[str]:
        t = text.lower()
        found = set()
        for norm, syns in self.location_synonyms.items():
            for s in syns:
                if s in t:
                    found.add(norm); break
        # các pattern chung
        patterns = [r'(?:address|location|city)[\s:]*([^\n]+)',
                    r'(?:địa chỉ|thành phố)[\s:]*([^\n]+)']
        for p in patterns:
            for m in re.findall(p, text, flags=re.IGNORECASE):
                ml = m.lower().strip()
                for norm, syns in self.location_synonyms.items():
                    if any(s in ml for s in syns):
                        found.add(norm)
        return sorted(found)

    def extract_experience(self, text: str):
        years = []
        for pat in [r'(\d+(?:\.\d+)?)\s*(?:years?|năm)\s*(?:of\s*)?(?:experience|exp)?',
                    r'experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:years?|năm)']:
            for m in re.findall(pat, text, flags=re.IGNORECASE):
                try: years.append(float(m))
                except: pass
        exp_years = max(years) if years else 0.0
        # titles:
        titles = re.findall(r'(?:^|\n)([A-Z][A-Za-z\s]+(?:Engineer|Developer|Manager|Analyst|Specialist|Lead))',
                            text, flags=re.MULTILINE)
        return {
            'exp_years': float(exp_years),
            'exp_months': int(exp_years * 12),
            'exp_spans': f"{int(exp_years)} years" if exp_years >= 1 else "0 years",
            'experience_entries': list(dict.fromkeys([t.strip() for t in titles]))[:5]
        }

    def extract_education(self, text: str) -> List[str]:
        entries = []
        for pat in [
            r'(?:Bachelor|Master|PhD|Degree)[\s]*(?:of|in)?[\s]*([^\n]+)',
            r'(?:University|College)[\s]*(?:of)?[\s]*([^\n]+)',
        ]:
            for m in re.findall(pat, text, flags=re.IGNORECASE):
                entries.append(m.strip())
        return entries[:3]

    def parse_cv(self, cv_text: str, filename: str | None = None) -> Dict:
        if not cv_text or not cv_text.strip():
            raise ValueError("CV text is empty")
        cand_id = f"{(filename or 'candidate')}_{uuid.uuid4().hex[:8]}"
        contact = self.extract_contact_info(cv_text)
        name = self.extract_name(cv_text)
        skills_dict = self.extract_skills(cv_text)
        locs = self.extract_locations(cv_text)
        exp = self.extract_experience(cv_text)
        edu = self.extract_education(cv_text)


        def capwords(s):
            if isinstance(s, str):
                s = re.sub(r"'s\b", "", s)
                return ' '.join(w.capitalize() for w in s.split())
            return s

        norm_name = capwords(name)
        norm_locs = [capwords(l) for l in locs]
        norm_edu = [capwords(e) for e in edu]
        norm_exp_entries = [capwords(e) for e in exp['experience_entries']]

        norm_tech_skills = [capwords(s) for s in skills_dict['technical_skills']]
        norm_soft_skills = [capwords(s) for s in skills_dict['soft_skills']]
        norm_buzzwords = [capwords(s) for s in skills_dict['buzzwords']]
        norm_all_skills = [capwords(s) for s in skills_dict['all_skills']]

        return {
            'cand_id': cand_id,
            'name': norm_name,
            'language': 'en',
            'emails': contact['emails'],
            'phones': contact['phones'],
            'links': [],
            'locations': norm_locs,
            'skills_norm': norm_tech_skills,
            'soft_skills': norm_soft_skills,
            'buzzwords': norm_buzzwords,
            'all_skills': norm_all_skills,
            'exp_months': exp['exp_months'],
            'exp_years': exp['exp_years'],
            'exp_spans': exp['exp_spans'],
            'experience_entries': norm_exp_entries,
            'education_entries': norm_edu,
            'certs': [],
            'resume_text': cv_text,
            'parsed_at': datetime.now().isoformat(),
        }

def parse_cv_file(file_content: str, filename: str | None = None) -> Dict:
    parser = CVParser()
    return parser.parse_cv(file_content, filename)
