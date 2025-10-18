import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { UploadCard } from '@/components/UploadCard'
import { ManualForm } from '@/components/ManualForm'
import { ResultCard } from '@/components/ResultCard'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Heart, Upload, AlertCircle, Stethoscope, Activity, ClipboardList } from 'lucide-react'
import { apiClient, type HeartDiseaseInput, type HeartDiseasePrediction } from './lib/api'

type AppState = 'upload' | 'manual' | 'result' | 'loading'

function App() {
  const [currentState, setCurrentState] = useState<AppState>('upload')
  const [prediction, setPrediction] = useState<HeartDiseasePrediction | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [extractedData, setExtractedData] = useState<HeartDiseaseInput | null>(null)

  const handleDataExtracted = (data: HeartDiseaseInput) => {
    setExtractedData(data)
    setCurrentState('manual')
    setError(null)
  }

  const handleFormSubmit = async (data: HeartDiseaseInput) => {
    setCurrentState('loading')
    setError(null)

    try {
      const result = await apiClient.predict(data)
      setPrediction(result)
      setCurrentState('result')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Prediction failed'
      setError(errorMessage)
      setCurrentState('manual')
    }
  }

  const handleError = (errorMessage: string) => {
    setError(errorMessage)
  }

  const handleReset = () => {
    setCurrentState('upload')
    setPrediction(null)
    setError(null)
    setExtractedData(null)
  }

  const renderContent = () => {
    switch (currentState) {
      case 'upload':
        return (
          <div className="space-y-6">
            <UploadCard 
              onDataExtracted={handleDataExtracted}
              onError={handleError}
            />
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-4">or</p>
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button 
                  onClick={() => setCurrentState('manual')}
                  className="w-full max-w-md bg-blue-600 hover:bg-blue-700 text-white hover:shadow-lg transition-shadow"
                >
                  <ClipboardList className="h-4 w-4 mr-2" />
                  Enter Health Data
                </Button>
              </motion.div>
            </div>
          </div>
        )

      case 'manual':
        return (
          <div className="space-y-6">
            <ManualForm 
              onSubmit={handleFormSubmit}
              onError={handleError}
              initialData={extractedData || undefined}
            />
            <div className="text-center">
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button 
                  onClick={() => setCurrentState('upload')}
                  variant="outline"
                  className="w-full max-w-md hover:shadow-lg transition-shadow"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Health Report Instead
                </Button>
              </motion.div>
            </div>
          </div>
        )

      case 'loading':
        return (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="w-full max-w-md mx-auto shadow-lg">
              <CardContent className="pt-6">
                <div className="text-center space-y-4">
                  <motion.div
                    className="flex justify-center"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  >
                    <div className="p-4 bg-blue-50 rounded-full">
                      <Stethoscope className="h-12 w-12 text-blue-600" />
                    </div>
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    <h3 className="text-lg font-semibold">Analyzing Your Data</h3>
                    <p className="text-sm text-muted-foreground">
                      Our AI model is processing your health information...
                    </p>
                  </motion.div>
                  <motion.div
                    className="flex justify-center space-x-1"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                  >
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        className="w-2 h-2 bg-blue-600 rounded-full"
                        animate={{
                          scale: [1, 1.5, 1],
                          opacity: [0.5, 1, 0.5],
                        }}
                        transition={{
                          duration: 1.5,
                          repeat: Infinity,
                          delay: i * 0.2,
                        }}
                      />
                    ))}
                  </motion.div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )

      case 'result':
        return prediction ? (
          <ResultCard 
            prediction={prediction}
            onReset={handleReset}
          />
        ) : null

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-20 left-10 w-32 h-32 bg-blue-100 rounded-full opacity-20"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        <motion.div
          className="absolute top-40 right-20 w-24 h-24 bg-green-100 rounded-full opacity-20"
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [360, 180, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        <motion.div
          className="absolute bottom-20 left-1/4 w-40 h-40 bg-green-100 rounded-full opacity-15"
          animate={{
            scale: [1, 1.3, 1],
            rotate: [0, -180, -360],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      </div>

      {/* Header */}
      <motion.header 
        className="bg-white/90 backdrop-blur-sm shadow-sm border-b relative z-10"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-center gap-4">
            <motion.div
              className="relative"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, duration: 0.6, type: "spring" }}
            >
              <div className="p-2 bg-blue-50 rounded-full">
                <Stethoscope className="h-8 w-8 text-blue-600" />
              </div>
            </motion.div>
            <motion.div 
              className="text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
                Heart Health Assessment
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Professional AI-powered cardiovascular risk evaluation
              </p>
            </motion.div>
            <motion.div
              className="flex space-x-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Activity className="h-6 w-6 text-green-500" />
              </motion.div>
            </motion.div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 relative z-10">
        {/* Error Display */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -20 }}
              transition={{ duration: 0.3 }}
              className="mb-6"
            >
              <Card className="border-red-200 bg-red-50 shadow-lg">
                <CardContent className="pt-6">
                  <div className="flex items-start gap-3">
                    <motion.div
                      animate={{ rotate: [0, -10, 10, 0] }}
                      transition={{ duration: 0.5, repeat: 2 }}
                    >
                      <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                    </motion.div>
                    <div>
                      <h3 className="font-semibold text-red-800">Error</h3>
                      <p className="text-sm text-red-700 mt-1">{error}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentState}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Footer */}
      <motion.footer 
        className="bg-white/80 backdrop-blur-sm border-t mt-16 relative z-10"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
      >
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-sm text-muted-foreground">
            <motion.div
              className="flex items-center justify-center gap-2 mb-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.4 }}
            >
              <AlertCircle className="h-4 w-4 text-orange-500" />
              <p>
                <strong>Medical Disclaimer:</strong> This tool is for educational purposes only and should not replace professional medical advice.
              </p>
            </motion.div>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.6 }}
            >
              Always consult a qualified healthcare professional for any health concerns.
            </motion.p>
          </div>
        </div>
      </motion.footer>
    </div>
  )
}

export default App
