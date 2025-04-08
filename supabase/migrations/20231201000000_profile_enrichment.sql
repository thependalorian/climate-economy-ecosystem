-- Add enrichment column to profiles table for storing profile enrichment data
ALTER TABLE IF EXISTS public.profiles
ADD COLUMN IF NOT EXISTS enrichment jsonb;

COMMENT ON COLUMN public.profiles.enrichment IS 'JSON data containing profile enrichment information like skills, extracted information, and enrichment status';

-- Create search_analytics table for tracking job search activity
CREATE TABLE IF NOT EXISTS public.search_analytics (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  search_query text,
  search_params jsonb,
  search_type text,
  result_count integer,
  created_at timestamp with time zone DEFAULT now(),
  
  CONSTRAINT search_analytics_user_id_fkey FOREIGN KEY (user_id)
    REFERENCES auth.users(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.search_analytics IS 'Records job search analytics for users';

-- Create RLS policies for search_analytics
ALTER TABLE public.search_analytics ENABLE ROW LEVEL SECURITY;

-- Users can insert their own search analytics
CREATE POLICY "Users can insert their own search analytics"
  ON public.search_analytics
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);
  
-- Users can view their own search analytics
CREATE POLICY "Users can view their own search analytics"
  ON public.search_analytics
  FOR SELECT
  USING (auth.uid() = user_id);

-- Admin users can view all search analytics
CREATE POLICY "Admin users can view all search analytics"
  ON public.search_analytics
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

-- Create sectors table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.sectors (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text NOT NULL UNIQUE,
  description text,
  created_at timestamp with time zone DEFAULT now()
);

COMMENT ON TABLE public.sectors IS 'Climate-related sectors for job categorization';

-- Create focus_areas table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.focus_areas (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text NOT NULL UNIQUE,
  sector_id uuid REFERENCES public.sectors(id),
  description text,
  created_at timestamp with time zone DEFAULT now()
);

COMMENT ON TABLE public.focus_areas IS 'Specific focus areas within climate sectors';

-- Enable RLS on sectors and focus_areas tables
ALTER TABLE public.sectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.focus_areas ENABLE ROW LEVEL SECURITY;

-- Everyone can read sectors and focus areas
CREATE POLICY "Everyone can read sectors"
  ON public.sectors
  FOR SELECT
  USING (true);

CREATE POLICY "Everyone can read focus areas"
  ON public.focus_areas
  FOR SELECT
  USING (true);

-- Only admins can insert, update, or delete sectors and focus areas
CREATE POLICY "Only admins can insert sectors"
  ON public.sectors
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

CREATE POLICY "Only admins can update sectors"
  ON public.sectors
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

CREATE POLICY "Only admins can delete sectors"
  ON public.sectors
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

CREATE POLICY "Only admins can insert focus areas"
  ON public.focus_areas
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

CREATE POLICY "Only admins can update focus areas"
  ON public.focus_areas
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

CREATE POLICY "Only admins can delete focus areas"
  ON public.focus_areas
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

-- Insert some initial sectors if they don't exist
INSERT INTO public.sectors (name, description)
VALUES 
  ('Renewable Energy', 'Clean energy sources like solar, wind, hydro, and geothermal'),
  ('Sustainable Agriculture', 'Farming practices that protect the environment and food security'),
  ('Clean Transportation', 'Low or zero emission vehicles and transportation systems'),
  ('Circular Economy', 'Reducing waste and regenerating natural systems'),
  ('Climate Finance', 'Financial activities aimed at climate change mitigation and adaptation'),
  ('Carbon Management', 'Technologies and processes to capture, store, and utilize carbon'),
  ('Water Solutions', 'Conservation, treatment, and management of water resources'),
  ('Green Building', 'Sustainable construction and building practices')
ON CONFLICT (name) DO NOTHING;

-- Insert some initial focus areas if they don't exist
INSERT INTO public.focus_areas (name, sector_id, description)
VALUES 
  ('Solar Energy', (SELECT id FROM public.sectors WHERE name = 'Renewable Energy'), 'Solar power technologies and infrastructure'),
  ('Wind Energy', (SELECT id FROM public.sectors WHERE name = 'Renewable Energy'), 'Wind power technologies and infrastructure'),
  ('Hydropower', (SELECT id FROM public.sectors WHERE name = 'Renewable Energy'), 'Hydroelectric power systems and management'),
  ('Regenerative Agriculture', (SELECT id FROM public.sectors WHERE name = 'Sustainable Agriculture'), 'Agricultural approaches that regenerate topsoil and enhance ecosystem services'),
  ('Precision Agriculture', (SELECT id FROM public.sectors WHERE name = 'Sustainable Agriculture'), 'Using technology to make farming more accurate and controlled'),
  ('Electric Vehicles', (SELECT id FROM public.sectors WHERE name = 'Clean Transportation'), 'Electric-powered vehicles and related infrastructure'),
  ('Public Transit', (SELECT id FROM public.sectors WHERE name = 'Clean Transportation'), 'Mass transit systems that reduce individual car usage'),
  ('Waste Reduction', (SELECT id FROM public.sectors WHERE name = 'Circular Economy'), 'Minimizing waste through recycling and reuse'),
  ('Product Lifecycle', (SELECT id FROM public.sectors WHERE name = 'Circular Economy'), 'Designing products for reuse and recycling'),
  ('ESG Investing', (SELECT id FROM public.sectors WHERE name = 'Climate Finance'), 'Investment strategies considering environmental, social, and governance factors'),
  ('Climate Risk Analysis', (SELECT id FROM public.sectors WHERE name = 'Climate Finance'), 'Assessing financial risks related to climate change'),
  ('Carbon Capture', (SELECT id FROM public.sectors WHERE name = 'Carbon Management'), 'Technologies to capture carbon dioxide from the atmosphere'),
  ('Carbon Utilization', (SELECT id FROM public.sectors WHERE name = 'Carbon Management'), 'Processes to convert captured carbon into useful products'),
  ('Water Conservation', (SELECT id FROM public.sectors WHERE name = 'Water Solutions'), 'Technologies and practices to reduce water consumption'),
  ('Water Treatment', (SELECT id FROM public.sectors WHERE name = 'Water Solutions'), 'Processing water to make it suitable for specific uses'),
  ('Sustainable Construction', (SELECT id FROM public.sectors WHERE name = 'Green Building'), 'Construction methods that minimize environmental impact'),
  ('Energy Efficiency', (SELECT id FROM public.sectors WHERE name = 'Green Building'), 'Building designs and systems that minimize energy use')
ON CONFLICT (name) DO NOTHING; 