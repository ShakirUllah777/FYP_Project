import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collabspace.settings')
django.setup()

from accounts.models import Skill

skills_to_add = [
    # 1. Programming Languages
    ('Python', 'programming'),
    ('JavaScript', 'programming'),
    ('TypeScript', 'programming'),
    ('C++', 'programming'),
    ('C#', 'programming'),
    ('Java', 'programming'),
    ('C', 'programming'),
    ('Go', 'programming'),
    ('Rust', 'programming'),
    ('PHP', 'programming'),
    ('Ruby', 'programming'),
    ('Swift', 'programming'),
    ('Kotlin', 'programming'),
    ('Dart', 'programming'),
    ('R', 'programming'),
    ('MATLAB', 'programming'),
    ('Scala', 'programming'),
    ('Bash / Shell', 'programming'),
    ('SQL', 'programming'),
    ('HTML5 / CSS3', 'programming'),
    ('Elixir', 'programming'),
    ('Haskell', 'programming'),
    ('Lua', 'programming'),
    ('Perl', 'programming'),

    # 2. Frameworks & Libraries
    ('React.js', 'frameworks'),
    ('Next.js', 'frameworks'),
    ('Vue.js', 'frameworks'),
    ('Angular', 'frameworks'),
    ('Node.js', 'frameworks'),
    ('Express.js', 'frameworks'),
    ('Django', 'frameworks'),
    ('Flask', 'frameworks'),
    ('FastAPI', 'frameworks'),
    ('Spring Boot', 'frameworks'),
    ('ASP.NET Core', 'frameworks'),
    ('Laravel', 'frameworks'),
    ('Ruby on Rails', 'frameworks'),
    ('Svelte', 'frameworks'),
    ('NestJS', 'frameworks'),
    ('Bootstrap', 'frameworks'),
    ('Tailwind CSS', 'frameworks'),
    ('jQuery', 'frameworks'),
    ('Redux', 'frameworks'),
    ('GraphQL', 'frameworks'),
    ('RESTful APIs', 'frameworks'),
    ('Electron.js', 'frameworks'),
    ('WebAssembly', 'frameworks'),

    # 3. AI, Data Science & Machine Learning
    ('Machine Learning', 'ai_data'),
    ('Deep Learning', 'ai_data'),
    ('Artificial Intelligence', 'ai_data'),
    ('Data Science', 'ai_data'),
    ('Data Analytics', 'ai_data'),
    ('Data Visualization', 'ai_data'),
    ('Natural Language Processing (NLP)', 'ai_data'),
    ('Computer Vision', 'ai_data'),
    ('PyTorch', 'ai_data'),
    ('TensorFlow', 'ai_data'),
    ('Keras', 'ai_data'),
    ('OpenCV', 'ai_data'),
    ('Scikit-Learn', 'ai_data'),
    ('Pandas & NumPy', 'ai_data'),
    ('Generative AI / LLMs', 'ai_data'),
    ('Prompt Engineering', 'ai_data'),
    ('RAG (Retrieval-Augmented Generation)', 'ai_data'),
    ('LangChain', 'ai_data'),
    ('Hugging Face', 'ai_data'),
    ('MLOps', 'ai_data'),
    ('Big Data & Spark', 'ai_data'),
    ('Tableau & Power BI', 'ai_data'),
    ('Reinforcement Learning', 'ai_data'),

    # 4. Databases & Storage
    ('PostgreSQL', 'databases'),
    ('MySQL', 'databases'),
    ('SQLite', 'databases'),
    ('MongoDB', 'databases'),
    ('Redis', 'databases'),
    ('Firebase / Firestore', 'databases'),
    ('Supabase', 'databases'),
    ('Oracle DB', 'databases'),
    ('Microsoft SQL Server', 'databases'),
    ('Cassandra', 'databases'),
    ('Neo4j (Graph DB)', 'databases'),
    ('Elasticsearch', 'databases'),
    ('DynamoDB', 'databases'),
    ('Vector Databases (Pinecone/Chroma)', 'databases'),

    # 5. DevOps & Cloud
    ('Docker', 'devops_cloud'),
    ('Kubernetes', 'devops_cloud'),
    ('Amazon Web Services (AWS)', 'devops_cloud'),
    ('Google Cloud Platform (GCP)', 'devops_cloud'),
    ('Microsoft Azure', 'devops_cloud'),
    ('CI/CD Pipelines', 'devops_cloud'),
    ('GitHub Actions', 'devops_cloud'),
    ('Jenkins', 'devops_cloud'),
    ('Terraform', 'devops_cloud'),
    ('Ansible', 'devops_cloud'),
    ('Linux Administration', 'devops_cloud'),
    ('Nginx / Apache', 'devops_cloud'),
    ('Microservices Architecture', 'devops_cloud'),
    ('Serverless Computing', 'devops_cloud'),

    # 6. Mobile Development
    ('Flutter', 'mobile'),
    ('React Native', 'mobile'),
    ('Android Development (Kotlin/Java)', 'mobile'),
    ('iOS Development (Swift/SwiftUI)', 'mobile'),
    ('Expo', 'mobile'),
    ('Ionic', 'mobile'),
    ('Cross-Platform Mobile Dev', 'mobile'),

    # 7. Web & UI/UX Design
    ('Frontend Development', 'web_design'),
    ('Backend Development', 'web_design'),
    ('Full Stack Development', 'web_design'),
    ('UI/UX Design', 'web_design'),
    ('Figma', 'web_design'),
    ('Adobe XD', 'web_design'),
    ('Wireframing & Prototyping', 'web_design'),
    ('Responsive Web Design', 'web_design'),
    ('WebSockets & Real-time Systems', 'web_design'),

    # 8. Cybersecurity & QA
    ('Software Testing / QA', 'security_qa'),
    ('Automated Testing (Selenium/Cypress)', 'security_qa'),
    ('Jest / Unit Testing', 'security_qa'),
    ('Cybersecurity', 'security_qa'),
    ('Ethical Hacking & Pen Testing', 'security_qa'),
    ('Network Security', 'security_qa'),
    ('Cryptography', 'security_qa'),
    ('OWASP Security Standards', 'security_qa'),

    # 9. Tools & Other Tech
    ('Git & GitHub', 'others'),
    ('System Design', 'others'),
    ('Software Architecture', 'others'),
    ('Agile / Scrum', 'others'),
    ('JIRA & Confluence', 'others'),
    ('Blockchain & Smart Contracts', 'others'),
    ('Web3 / Solidity', 'others'),
    ('Internet of Things (IoT)', 'others'),
    ('Embedded Systems (Arduino/Raspberry Pi)', 'others'),
    ('Game Development (Unity/Unreal Engine)', 'others'),
    ('Object-Oriented Programming (OOP)', 'others'),
    ('Data Structures & Algorithms', 'others'),
]

added_count = 0
updated_count = 0
for name, category in skills_to_add:
    obj, created = Skill.objects.get_or_create(name=name, defaults={'category': category})
    if created:
        added_count += 1
    elif obj.category != category:
        obj.category = category
        obj.save()
        updated_count += 1

print(f"Added {added_count} new skills, updated category for {updated_count} skills.")

