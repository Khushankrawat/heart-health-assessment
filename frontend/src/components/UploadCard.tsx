import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, Image, AlertCircle, CheckCircle, Stethoscope, Activity, Zap } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiClient, type HeartDiseaseInput, type UploadResponse } from '@/lib/api'

interface UploadCardProps {
  onDataExtracted: (data: HeartDiseaseInput) => void
  onError: (error: string) => void
}

export function UploadCard({ onDataExtracted, onError }: UploadCardProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setIsUploading(true)
    setUploadResult(null)

    try {
      const result = await apiClient.uploadFile(file)
      setUploadResult(result)

      if (result.success && result.extracted_data) {
        onDataExtracted(result.extracted_data)
      } else {
        onError(result.message)
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed'
      onError(errorMessage)
    } finally {
      setIsUploading(false)
    }
  }, [onDataExtracted, onError])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  const handleSubmitExtracted = () => {
    if (uploadResult?.extracted_data) {
      onDataExtracted(uploadResult.extracted_data)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="w-full max-w-2xl mx-auto shadow-lg hover:shadow-xl transition-shadow duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <motion.div
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Stethoscope className="h-5 w-5 text-blue-600" />
            </motion.div>
            Medical Report Upload
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <Activity className="h-4 w-4 text-green-500" />
            </motion.div>
          </CardTitle>
          <CardDescription>
            Upload your medical reports (PDF, JPG, or PNG) for automated health data extraction.
            Maximum file size: 10MB
          </CardDescription>
        </CardHeader>
      <CardContent className="space-y-4">
        <AnimatePresence>
          {!uploadResult && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              <div
                {...getRootProps()}
                className={`
                  border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-300
                  ${isDragActive ? 'border-primary bg-primary/5 scale-105' : 'border-muted-foreground/25'}
                  ${isUploading ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary hover:bg-primary/5 hover:scale-102'}
                `}
              >
                <input {...getInputProps()} />
                <div className="space-y-4">
                  <div className="flex justify-center">
                    {isUploading ? (
                      <motion.div 
                        className="relative w-12 h-12"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      >
                        <div className="absolute inset-0 rounded-full border-4 border-blue-200"></div>
                        <div className="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent"></div>
                      </motion.div>
                    ) : (
                      <motion.div 
                        className="flex gap-2"
                        animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
                        transition={{ duration: 0.2 }}
                      >
                        <motion.div
                          animate={{ rotate: [0, 5, -5, 0] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        >
                          <FileText className="h-12 w-12 text-blue-500" />
                        </motion.div>
                        <motion.div
                          animate={{ rotate: [0, -5, 5, 0] }}
                          transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                        >
                          <Image className="h-12 w-12 text-green-500" />
                        </motion.div>
                      </motion.div>
                    )}
                  </div>
                  <motion.div
                    animate={isDragActive ? { y: -5 } : { y: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <p className="text-lg font-medium">
                      {isUploading ? 'Processing...' : isDragActive ? 'Drop the file here' : 'Drag & drop your health report here'}
                    </p>
                    <p className="text-sm text-muted-foreground mt-2">
                      or click to select a file
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Supports: PDF, JPG, PNG (max 10MB)
                    </p>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {uploadResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="space-y-4"
            >
              <motion.div 
                className={`p-4 rounded-lg flex items-start gap-3 ${
                  uploadResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                }`}
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2 }}
              >
                <motion.div
                  animate={uploadResult.success ? 
                    { rotate: [0, 10, -10, 0], scale: [1, 1.1, 1] } : 
                    { rotate: [0, -10, 10, 0] }
                  }
                  transition={{ duration: 0.5, repeat: 2 }}
                >
                  {uploadResult.success ? (
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                  )}
                </motion.div>
                <div>
                  <p className={`font-medium ${
                    uploadResult.success ? 'text-green-800' : 'text-red-800'
                  }`}>
                    {uploadResult.success ? 'Data Extracted Successfully!' : 'Extraction Failed'}
                  </p>
                  <p className={`text-sm mt-1 ${
                    uploadResult.success ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {uploadResult.message}
                  </p>
                  {uploadResult.confidence && (
                    <motion.p 
                      className="text-xs mt-1 text-muted-foreground"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.5 }}
                    >
                      Confidence: {(uploadResult.confidence * 100).toFixed(0)}%
                    </motion.p>
                  )}
                </div>
              </motion.div>

            {uploadResult.success && uploadResult.extracted_data && (
              <div className="space-y-3">
                <h4 className="font-medium">Extracted Data Preview:</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div><span className="font-medium">Age:</span> {uploadResult.extracted_data.age}</div>
                  <div><span className="font-medium">Gender:</span> {uploadResult.extracted_data.gender}</div>
                  <div><span className="font-medium">Cholesterol:</span> {uploadResult.extracted_data.cholesterol}</div>
                  <div><span className="font-medium">Blood Pressure:</span> {uploadResult.extracted_data.blood_pressure}</div>
                  <div><span className="font-medium">Heart Rate:</span> {uploadResult.extracted_data.heart_rate}</div>
                  <div><span className="font-medium">Smoking:</span> {uploadResult.extracted_data.smoking}</div>
                </div>
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Button onClick={handleSubmitExtracted} className="w-full">
                    <Zap className="h-4 w-4 mr-2" />
                    Use Extracted Data for Prediction
                  </Button>
                </motion.div>
              </div>
            )}

            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Button
                variant="outline"
                onClick={() => setUploadResult(null)}
                className="w-full"
              >
                Upload Another File
              </Button>
            </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
    </motion.div>
  )
}
