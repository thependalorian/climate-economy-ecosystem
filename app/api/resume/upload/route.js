import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { OpenAI } from 'openai';
import { v4 as uuidv4 } from 'uuid';

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

// Only create client if credentials are available
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

// Validate Supabase client
if (!supabase) {
  console.warn('Supabase client not initialized. Check your environment variables.');
}

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');
    const userId = formData.get('userId') || 'anonymous';

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Check file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: 'Invalid file type. Please upload a PDF or Word document.' },
        { status: 400 }
      );
    }

    // Check file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      return NextResponse.json(
        { error: 'File too large. Maximum size is 5MB.' },
        { status: 400 }
      );
    }

    // Convert file to buffer
    const buffer = Buffer.from(await file.arrayBuffer());

    // Upload file to Supabase Storage
    const fileName = `${userId}_${uuidv4()}_${file.name}`;
    const { data: uploadData, error: uploadError } = await supabase
      .storage
      .from('resumes')
      .upload(fileName, buffer, {
        contentType: file.type,
        upsert: false
      });

    if (uploadError) {
      console.error('Error uploading file:', uploadError);
      return NextResponse.json(
        { error: 'Failed to upload file' },
        { status: 500 }
      );
    }

    // Get public URL for the uploaded file
    const { data: { publicUrl } } = supabase
      .storage
      .from('resumes')
      .getPublicUrl(fileName);

    // Analyze the resume (simulated for now)
    // In a real implementation, you would use OpenAI or another service to extract information
    const analysisResults = {
      fileName: file.name,
      fileSize: file.size,
      uploadDate: new Date().toISOString(),
      skills: ['Solar Panel Installation', 'Electrical Wiring', 'Project Management'],
      experience: [
        { title: 'Solar Technician', company: 'Green Energy Solutions', years: 2 },
        { title: 'Electrical Apprentice', company: 'City Power', years: 1 }
      ],
      education: [
        { degree: 'Associate of Science', field: 'Electrical Technology', institution: 'Community College' }
      ]
    };

    // Store the analysis results in Supabase
    const { data: analysisData, error: analysisError } = await supabase
      .from('resume_analyses')
      .insert([
        {
          user_id: userId,
          file_name: file.name,
          file_url: publicUrl,
          analysis_results: analysisResults,
          created_at: new Date().toISOString()
        }
      ]);

    if (analysisError) {
      console.error('Error storing analysis results:', analysisError);
    }

    return NextResponse.json({
      success: true,
      fileName: file.name,
      fileUrl: publicUrl,
      analysisResults
    });

  } catch (error) {
    console.error('Error processing file upload:', error);
    return NextResponse.json(
      { error: 'Failed to process file upload' },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
