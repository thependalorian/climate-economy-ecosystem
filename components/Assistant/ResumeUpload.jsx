"use client"

import { useState } from 'react'
import { Button } from '../ui/Button'
import { Progress } from '../ui/progress'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog'
import { FiUpload, FiCheckCircle, FiAlertCircle } from 'react-icons/fi'

const ResumeUpload = ({ onUploadComplete }) => {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [error, setError] = useState('')
  const [showDialog, setShowDialog] = useState(false)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    
    if (!selectedFile) return
    
    if (!['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      .includes(selectedFile.type)) {
      setError('Please upload a PDF or Word document')
      return
    }
    
    if (selectedFile.size > 5 * 1024 * 1024) { // 5MB limit
      setError('File size should be less than 5MB')
      return
    }
    
    setFile(selectedFile)
    setError('')
  }

  const simulateUploadProgress = () => {
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      setUploadProgress(progress)
      
      if (progress >= 100) {
        clearInterval(interval)
        setUploading(false)
        setUploadSuccess(true)
        
        // Call the callback with mock data
        if (onUploadComplete) {
          onUploadComplete({
            fileName: file.name,
            fileSize: file.size,
            uploadDate: new Date().toISOString(),
            skills: ['Solar Panel Installation', 'Electrical Wiring', 'Project Management'],
            experience: [
              { title: 'Solar Technician', company: 'Green Energy Solutions', years: 2 },
              { title: 'Electrical Apprentice', company: 'City Power', years: 1 }
            ]
          })
        }
      }
    }, 300)
  }

  const handleUpload = async () => {
    if (!file) return
    
    setUploading(true)
    setUploadProgress(0)
    
    try {
      // In a real implementation, this would be an API call to upload the file
      // For now, we'll simulate the upload process
      simulateUploadProgress()
    } catch (err) {
      setError('Failed to upload file. Please try again.')
      setUploading(false)
    }
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
        <div className="flex flex-col items-center justify-center text-center">
          <div className="mb-4">
            <FiUpload className="text-4xl text-primary" />
          </div>
          <h3 className="text-xl font-bold mb-2">Upload Your Resume</h3>
          <p className="text-sm text-gray-600 mb-4">
            Upload your resume to get personalized job and training recommendations
          </p>
          
          <div className="w-full">
            <div className="flex items-center justify-center w-full">
              <label 
                className="flex flex-col w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50"
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault()
                  handleFileChange({ target: { files: e.dataTransfer.files } })
                }}
              >
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">PDF or Word (max. 5MB)</p>
                </div>
                <input 
                  type="file" 
                  className="hidden" 
                  accept=".pdf,.doc,.docx" 
                  onChange={handleFileChange}
                />
              </label>
            </div>
            
            {error && (
              <div className="mt-2 text-red-500 text-xs flex items-center">
                <FiAlertCircle className="mr-1" />
                {error}
              </div>
            )}
            
            {file && !uploading && !uploadSuccess && (
              <div className="mt-4 flex items-center justify-between bg-gray-50 p-2 rounded">
                <span className="text-sm truncate max-w-[200px]">{file.name}</span>
                <Button 
                  onClick={handleUpload}
                  className="btn btn-primary btn-sm"
                >
                  Upload
                </Button>
              </div>
            )}
            
            {uploading && (
              <div className="mt-4">
                <div className="mb-1 text-sm flex justify-between">
                  <span>Uploading...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} className="h-2" />
              </div>
            )}
            
            {uploadSuccess && (
              <div className="mt-4 flex items-center text-green-600">
                <FiCheckCircle className="mr-2" />
                <span className="text-sm font-medium">Resume uploaded successfully!</span>
                <button 
                  className="ml-auto text-primary text-sm" 
                  onClick={() => setShowDialog(true)}
                >
                  View Details
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Resume Upload Complete</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-gray-700 mb-4">We've analyzed your resume and identified the following:</p>
            
            <div className="mb-4">
              <h4 className="font-medium text-sm mb-2">Skills Identified:</h4>
              <div className="flex flex-wrap gap-2">
                {['Solar Panel Installation', 'Electrical Wiring', 'Project Management'].map(skill => (
                  <span key={skill} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
            
            <div className="mb-4">
              <h4 className="font-medium text-sm mb-2">Experience:</h4>
              <ul className="text-sm space-y-2">
                <li className="flex justify-between">
                  <span>Solar Technician at Green Energy Solutions</span>
                  <span className="text-gray-500">2 years</span>
                </li>
                <li className="flex justify-between">
                  <span>Electrical Apprentice at City Power</span>
                  <span className="text-gray-500">1 year</span>
                </li>
              </ul>
            </div>
          </div>
          <DialogFooter>
            <Button onClick={() => setShowDialog(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default ResumeUpload 