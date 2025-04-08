'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import MainLayout from '@/components/layout/MainLayout';

/**
 * Resume Upload Page
 * 
 * Allows users to upload their resume for analysis and profile enhancement
 */
export default function ResumeUploadPage() {
  const [file, setFile] = useState(null);
  const [resumeText, setResumeText] = useState('');
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const fileInputRef = useRef(null);
  const { toast } = useToast();
  const router = useRouter();
  const supabase = createClientComponentClient();
  
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    
    // Check file type
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!validTypes.includes(selectedFile.type)) {
      toast({
        title: "Invalid file type",
        description: "Please upload a PDF, DOC, DOCX, or TXT file.",
        variant: "destructive",
      });
      return;
    }
    
    // Check file size (max 5MB)
    if (selectedFile.size > 5 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Please upload a file smaller than 5MB.",
        variant: "destructive",
      });
      return;
    }
    
    setFile(selectedFile);
  };
  
  const handleUpload = async () => {
    if (!file && !resumeText.trim()) {
      toast({
        title: "No resume provided",
        description: "Please upload a file or paste your resume text.",
        variant: "destructive",
      });
      return;
    }
    
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError) throw sessionError;
      
      if (!session) {
        router.push('/auth/signin');
        return;
      }
      
      const userId = session.user.id;
      
      if (file) {
        // Upload file
        setUploading(true);
        
        const fileExt = file.name.split('.').pop();
        const fileName = `${userId}-${Date.now()}.${fileExt}`;
        const filePath = `resumes/${fileName}`;
        
        const { error: uploadError } = await supabase.storage
          .from('user-documents')
          .upload(filePath, file);
        
        if (uploadError) throw uploadError;
        
        // Get public URL
        const { data: urlData } = supabase.storage
          .from('user-documents')
          .getPublicUrl(filePath);
        
        // Analyze resume
        setAnalyzing(true);
        setUploading(false);
        
        const response = await fetch('/api/profile/resume/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            userId,
            resumeUrl: urlData.publicUrl,
            fileType: fileExt
          }),
        });
        
        if (!response.ok) throw new Error('Failed to analyze resume');
        
        setAnalyzing(false);
        setUploadSuccess(true);
        
        toast({
          title: "Resume uploaded successfully",
          description: "Your resume has been analyzed and your profile has been updated.",
          variant: "default",
        });
        
        // Redirect to profile page after 2 seconds
        setTimeout(() => {
          router.push('/profile');
        }, 2000);
      } else if (resumeText.trim()) {
        // Analyze pasted text
        setAnalyzing(true);
        
        const response = await fetch('/api/profile/resume/analyze-text', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            userId,
            resumeText: resumeText.trim()
          }),
        });
        
        if (!response.ok) throw new Error('Failed to analyze resume text');
        
        setAnalyzing(false);
        setUploadSuccess(true);
        
        toast({
          title: "Resume text analyzed successfully",
          description: "Your resume has been analyzed and your profile has been updated.",
          variant: "default",
        });
        
        // Redirect to profile page after 2 seconds
        setTimeout(() => {
          router.push('/profile');
        }, 2000);
      }
    } catch (error) {
      console.error('Error uploading resume:', error);
      
      setUploading(false);
      setAnalyzing(false);
      
      toast({
        title: "Error uploading resume",
        description: error.message || "An error occurred while uploading your resume.",
        variant: "destructive",
      });
    }
  };
  
  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Upload Your Resume</h1>
        
        <Card className="p-6 mb-6">
          <div className="space-y-4">
            <p className="text-gray-600">
              Upload your resume to automatically extract your skills, experience, and education.
              This information will be used to enhance your profile and provide better job recommendations.
            </p>
            
            {uploadSuccess ? (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-green-800">Resume processed successfully!</h3>
                  <p className="text-green-700 mt-1">
                    Your resume has been analyzed and your profile has been updated.
                    Redirecting to your profile...
                  </p>
                </div>
              </div>
            ) : (
              <>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <div className="flex flex-col items-center">
                    <Upload className="h-10 w-10 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium mb-2">Upload Resume File</h3>
                    <p className="text-sm text-gray-500 mb-4">
                      Drag and drop your resume file here, or click to browse
                    </p>
                    <Input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.doc,.docx,.txt"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                    <Button
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploading || analyzing}
                    >
                      Select File
                    </Button>
                    {file && (
                      <div className="mt-4 flex items-center text-sm text-gray-600">
                        <FileText className="h-4 w-4 mr-2" />
                        {file.name}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="text-center text-gray-500 my-4">OR</div>
                
                <div>
                  <h3 className="text-lg font-medium mb-2">Paste Resume Text</h3>
                  <Textarea
                    placeholder="Paste your resume text here..."
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                    rows={10}
                    disabled={uploading || analyzing}
                  />
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start">
                  <AlertCircle className="h-5 w-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
                  <div>
                    <h3 className="font-medium text-blue-800">Privacy Notice</h3>
                    <p className="text-blue-700 mt-1">
                      Your resume will be processed to extract relevant information for your profile.
                      This data will only be used to provide personalized job recommendations and will not be shared with third parties.
                    </p>
                  </div>
                </div>
                
                <div className="flex justify-end">
                  <Button
                    onClick={handleUpload}
                    disabled={(!file && !resumeText.trim()) || uploading || analyzing}
                  >
                    {uploading ? 'Uploading...' : analyzing ? 'Analyzing...' : 'Upload Resume'}
                  </Button>
                </div>
              </>
            )}
          </div>
        </Card>
      </div>
    </MainLayout>
  );
}
