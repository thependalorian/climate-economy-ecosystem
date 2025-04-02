-- Seed data for credential evaluation services
INSERT INTO credential_services (name, url, description, is_naces_member, serves_clean_energy, massachusetts_specific, processing_time, approximate_cost)
VALUES
    ('World Education Services (WES)', 'https://www.wes.org/', 'WES is a non-profit organization that evaluates and advocates for the recognition of international educational qualifications.', TRUE, FALSE, FALSE, '7-10 business days (standard)', '$100-$205'),
    
    ('Educational Credential Evaluators (ECE)', 'https://www.ece.org/', 'ECE provides credential evaluations for individuals who have studied outside of the United States.', TRUE, FALSE, FALSE, '5 business days (standard)', '$90-$195'),
    
    ('SpanTran: The Evaluation Company', 'https://www.spantran.com/', 'SpanTran specializes in evaluating international academic credentials for educational, immigration and employment purposes.', TRUE, FALSE, FALSE, '2-10 business days', '$85-$250'),
    
    ('Foundation for International Services (FIS)', 'https://www.fis-web.com/', 'FIS evaluates credentials from any country to determine their U.S. equivalents.', TRUE, FALSE, FALSE, '5-15 business days', '$85-$245'),
    
    ('Massachusetts Clean Energy Center Credentials Support', 'https://www.masscec.com/credentials', 'MassCEC offers specialized support for international credential recognition in the clean energy sector.', FALSE, TRUE, TRUE, 'Varies', 'Free consultation'),
    
    ('Massachusetts Department of Professional Licensure', 'https://www.mass.gov/orgs/division-of-professional-licensure', 'State agency that oversees licensing for more than 167 trades and professions.', FALSE, FALSE, TRUE, 'Varies by profession', 'Varies by license type'),
    
    ('Boston Welcome Back Center', 'https://www.bhcc.edu/welcomeback/', 'Career counseling and educational case management to internationally educated nurses and other healthcare professionals.', FALSE, FALSE, TRUE, 'Ongoing support', 'Free services');

-- Seed data for education equivalencies
INSERT INTO education_equivalencies (country, original_credential, us_equivalent, education_level, notes)
VALUES
    -- Nigeria
    ('Nigeria', 'Bachelor of Engineering', 'Bachelor of Science in Engineering', 'Undergraduate', 'Recognized 5-year engineering degree from accredited Nigerian universities'),
    ('Nigeria', 'Higher National Diploma (HND)', 'Associate Degree', 'Undergraduate', 'Polytechnic qualification equivalent to Associate Degree in the US system'),
    ('Nigeria', 'National Diploma (ND)', 'Certificate', 'Undergraduate', 'Two-year polytechnic program, partial Associate Degree equivalent'),
    ('Nigeria', 'Master of Engineering', 'Master of Engineering/Master of Science', 'Graduate', 'Recognized post-graduate engineering qualification'),
    
    -- India
    ('India', 'Bachelor of Technology (B.Tech)', 'Bachelor of Science in Engineering', 'Undergraduate', 'Four-year engineering degree from recognized institutions'),
    ('India', 'Bachelor of Engineering (B.E.)', 'Bachelor of Science in Engineering', 'Undergraduate', 'Four-year engineering degree equivalent'),
    ('India', 'Master of Technology (M.Tech)', 'Master of Science in Engineering', 'Graduate', 'Recognized post-graduate engineering qualification'),
    ('India', 'Diploma in Engineering', 'Certificate/Partial Associate Degree', 'Undergraduate', 'Three-year diploma from polytechnic institutions'),
    
    -- Ghana
    ('Ghana', 'Bachelor of Science', 'Bachelor of Science', 'Undergraduate', 'Four-year degree from recognized Ghanaian universities'),
    ('Ghana', 'Higher National Diploma (HND)', 'Associate Degree', 'Undergraduate', 'Three-year polytechnic qualification'),
    
    -- Kenya
    ('Kenya', 'Bachelor of Technology', 'Bachelor of Science', 'Undergraduate', 'Four-year degree from recognized Kenyan universities'),
    ('Kenya', 'Diploma in Technology', 'Certificate/Partial Associate Degree', 'Undergraduate', 'Technical training certification'),
    
    -- UK
    ('UK', 'Master of Engineering (MEng)', 'Bachelor of Science in Engineering + Partial Master\'s', 'Undergraduate/Graduate', 'Four-year integrated master\'s program'),
    ('UK', 'Bachelor of Engineering (BEng)', 'Bachelor of Science in Engineering', 'Undergraduate', 'Three-year engineering degree'),
    ('UK', 'Higher National Diploma (HND)', 'Associate Degree', 'Undergraduate', 'Two-year vocational qualification'),
    
    -- Brazil
    ('Brazil', 'Bacharelado', 'Bachelor\'s Degree', 'Undergraduate', 'Four to six year undergraduate degree'),
    ('Brazil', 'Licenciatura', 'Bachelor\'s Degree in Education', 'Undergraduate', 'Teaching qualification'),
    ('Brazil', 'Tecnólogo', 'Associate Degree', 'Undergraduate', 'Short-cycle higher education program'),
    
    -- Mexico
    ('Mexico', 'Licenciatura', 'Bachelor\'s Degree', 'Undergraduate', 'Four to five year undergraduate degree'),
    ('Mexico', 'Técnico Superior Universitario', 'Associate Degree', 'Undergraduate', 'Two to three year technical degree'),
    
    -- Germany
    ('Germany', 'Diplom-Ingenieur', 'Master of Science in Engineering', 'Graduate', 'Traditional five-year engineering degree'),
    ('Germany', 'Bachelor of Engineering', 'Bachelor of Science in Engineering', 'Undergraduate', 'More recent three-year Bologna-compliant degree'),
    
    -- France
    ('France', 'Diplôme d\'Ingénieur', 'Master of Science in Engineering', 'Graduate', 'Five-year engineering degree from Grande École'),
    ('France', 'Licence', 'Bachelor\'s Degree', 'Undergraduate', 'Three-year undergraduate degree'),
    ('France', 'BTS (Brevet de Technicien Supérieur)', 'Associate Degree', 'Undergraduate', 'Two-year technical qualification'),
    
    -- Philippines
    ('Philippines', 'Bachelor of Science in Engineering', 'Bachelor of Science in Engineering', 'Undergraduate', 'Four to five year engineering degree'),
    ('Philippines', 'Associate in Engineering', 'Associate Degree', 'Undergraduate', 'Two-year undergraduate program');

-- Clean energy specific credential annotations
CREATE TABLE IF NOT EXISTS clean_energy_credential_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country TEXT NOT NULL,
    field TEXT NOT NULL,
    clean_energy_relevance TEXT NOT NULL,
    recommended_certifications TEXT[],
    massachusetts_specifics TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert clean energy credential notes
INSERT INTO clean_energy_credential_notes (country, field, clean_energy_relevance, recommended_certifications, massachusetts_specifics)
VALUES
    ('Nigeria', 'Electrical Engineering', 'High', 
     ARRAY['NABCEP PV Installation Professional', 'NABCEP PV Design Specialist', 'LEED Green Associate'], 
     'Nigerian electrical engineering degrees are generally recognized, but will require state licensure for professional engineering work. Foreign-educated engineers often need to pass FE and PE exams.'),
    
    ('India', 'Mechanical Engineering', 'High', 
     ARRAY['ASHRAE Certifications', 'AEE Certified Energy Manager', 'LEED AP BD+C'], 
     'Indian mechanical engineering degrees from top institutions are well-regarded. Additional training in state building codes and energy efficiency standards will be beneficial.'),
    
    ('Ghana', 'Civil Engineering', 'Medium', 
     ARRAY['LEED AP', 'BPI Building Analyst', 'OSHA Certifications'], 
     'Ghanaian civil engineering graduates should focus on Massachusetts building codes and energy efficiency standards. Additional coursework in sustainable design may be helpful.'),
    
    ('Kenya', 'Environmental Science', 'Medium', 
     ARRAY['ISSP Sustainability Associate', 'LEED Green Associate', 'Environmental Professional Certification'], 
     'Kenyan environmental science degrees translate well to sustainability roles in clean energy. Additional training in Massachusetts environmental regulations recommended.'),
    
    ('UK', 'Electrical Engineering', 'High', 
     ARRAY['NABCEP Certifications', 'OSHA Certifications'], 
     'UK electrical engineering degrees are well-recognized in Massachusetts. Becoming familiar with National Electrical Code (NEC) and Massachusetts amendments is crucial.'),
    
    ('Brazil', 'Renewable Energy Engineering', 'High', 
     ARRAY['NABCEP PV Installation Professional', 'BPI Building Analyst', 'AEE Renewable Energy Professional'], 
     'Brazilian renewable energy credentials are recognized but may require additional verification. Focus on Massachusetts-specific incentive programs and interconnection standards.'),
    
    ('Mexico', 'Energy Engineering', 'High', 
     ARRAY['AEE Certified Energy Manager', 'NABCEP Certifications', 'LEED AP'], 
     'Mexican energy engineering degrees require verification. Familiarity with Massachusetts energy codes and utility interconnection requirements is essential.'),
    
    ('Germany', 'Mechanical Engineering', 'High', 
     ARRAY['ASHRAE Certifications', 'AEE Energy Manager', 'Building Operator Certification'], 
     'German mechanical engineering degrees are highly regarded. Focus on US/Massachusetts-specific codes and standards for HVAC and building systems.'),
    
    ('France', 'Electrical Engineering', 'High', 
     ARRAY['NABCEP Certifications', 'UL PV System Installation Certification'], 
     'French engineering degrees from "Grande Écoles" are well-respected. Additional certification in US electrical codes and standards is recommended.'),
    
    ('Philippines', 'Civil Engineering', 'Medium', 
     ARRAY['LEED Certifications', 'BPI Building Analyst', 'OSHA Certifications'], 
     'Philippine engineering degrees require verification. Additional coursework in US building codes and energy efficiency standards is strongly recommended.'); 