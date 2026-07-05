"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Brain, MessageSquare, Database, BarChart3, Sparkles, Zap } from "lucide-react"

export default function Home() {
  const [userId, setUserId] = useState("demo_user")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [chatHistory, setChatHistory] = useState<Array<{role: string, content: string}>>([])

  const analyzeEmotion = async () => {
    if (!message.trim()) return
    
    setLoading(true)
    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: message,
          user_id: userId,
          context: message
        })
      })
      
      const data = await response.json()
      setResult(data)
      setChatHistory([...chatHistory, { role: "user", content: message }, { role: "assistant", content: JSON.stringify(data, null, 2) }])
      setMessage("")
    } catch (error) {
      console.error("Error:", error)
    } finally {
      setLoading(false)
    }
  }

  const comparePredictions = async () => {
    if (!message.trim()) return
    
    setLoading(true)
    try {
      const response = await fetch("/api/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: message,
          user_id: userId,
          context: message
        })
      })
      
      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error("Error:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="border-b bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600">
                <Brain className="h-7 w-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  EmoMemory
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  AI That Never Forgets
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
                <span className="mr-1.5 h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                Online
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <Tabs defaultValue="chat" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-[600px] mx-auto">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Chat
            </TabsTrigger>
            <TabsTrigger value="compare" className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Compare
            </TabsTrigger>
            <TabsTrigger value="memory" className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              Memory
            </TabsTrigger>
            <TabsTrigger value="about" className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              About
            </TabsTrigger>
          </TabsList>

          {/* Chat Tab */}
          <TabsContent value="chat" className="space-y-6">
            <Card className="border-2 shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-blue-600" />
                  Memory-Enabled Chat
                </CardTitle>
                <CardDescription>
                  Chat with EmoMemory and watch it remember your emotional context across conversations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">User ID</label>
                  <Input
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="Enter your user ID"
                    className="max-w-md"
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Your Message</label>
                  <Textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message here..."
                    rows={4}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault()
                        analyzeEmotion()
                      }
                    }}
                  />
                </div>

                <Button 
                  onClick={analyzeEmotion} 
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  {loading ? "Analyzing..." : "Analyze Emotion"}
                </Button>

                {result && (
                  <div className="mt-6 rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 p-6 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-800">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <Brain className="h-5 w-5 text-blue-600" />
                      Analysis Result
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600 dark:text-gray-400">Detected Emotion:</span>
                        <span className="text-2xl font-bold text-blue-600 dark:text-blue-400 capitalize">
                          {result.emotion}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600 dark:text-gray-400">Confidence:</span>
                        <span className="text-xl font-semibold text-purple-600 dark:text-purple-400">
                          {(result.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600 dark:text-gray-400">Memory Context:</span>
                        <span className={`font-semibold ${result.stateful ? 'text-green-600 dark:text-green-400' : 'text-gray-500'}`}>
                          {result.stateful ? "✓ Active" : "✗ None"}
                        </span>
                      </div>
                      {result.all_emotions && (
                        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                          <p className="text-sm font-medium mb-2">All Emotions:</p>
                          <div className="grid grid-cols-2 gap-2">
                            {Object.entries(result.all_emotions).map(([emotion, score]) => (
                              <div key={emotion} className="flex justify-between text-sm">
                                <span className="capitalize">{emotion}:</span>
                                <span className="font-medium">{(score * 100).toFixed(1)}%</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {chatHistory.length > 0 && (
                  <div className="mt-6 space-y-3">
                    <h3 className="text-lg font-semibold">Conversation History</h3>
                    <div className="max-h-96 overflow-y-auto space-y-2">
                      {chatHistory.map((msg, i) => (
                        <div
                          key={i}
                          className={`p-3 rounded-lg ${
                            msg.role === "user"
                              ? "bg-blue-100 dark:bg-blue-900/30 ml-8"
                              : "bg-purple-100 dark:bg-purple-900/30 mr-8"
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Compare Tab */}
          <TabsContent value="compare" className="space-y-6">
            <Card className="border-2 shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-purple-600" />
                  Stateless vs Stateful Comparison
                </CardTitle>
                <CardDescription>
                  See the difference between traditional AI (no memory) and EmoMemory (with Cognee)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">User ID</label>
                  <Input
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="Enter your user ID"
                    className="max-w-md"
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Your Message</label>
                  <Textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message here..."
                    rows={4}
                  />
                </div>

                <Button 
                  onClick={comparePredictions} 
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                >
                  {loading ? "Comparing..." : "Compare Predictions"}
                </Button>

                {result && (
                  <div className="mt-6 grid md:grid-cols-2 gap-4">
                    <Card className="bg-gray-50 dark:bg-gray-800/50">
                      <CardHeader>
                        <CardTitle className="text-lg">Without Memory</CardTitle>
                        <CardDescription>Traditional stateless AI</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <p className="text-2xl font-bold capitalize">{result.stateless?.emotion}</p>
                          <p className="text-gray-600 dark:text-gray-400">
                            Confidence: {(result.stateless?.confidence * 100).toFixed(1)}%
                          </p>
                          <p className="text-sm text-gray-500">No context from past interactions</p>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-2 border-blue-200 dark:border-blue-800">
                      <CardHeader>
                        <CardTitle className="text-lg text-blue-600 dark:text-blue-400">With Memory</CardTitle>
                        <CardDescription>Powered by Cognee</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <p className="text-2xl font-bold capitalize text-blue-600 dark:text-blue-400">
                            {result.stateful?.emotion}
                          </p>
                          <p className="text-gray-600 dark:text-gray-400">
                            Confidence: {(result.stateful?.confidence * 100).toFixed(1)}%
                          </p>
                          {result.stateful?.has_context && (
                            <p className="text-sm text-green-600 dark:text-green-400 font-medium">
                              ✓ Using {result.stateful.memory_context?.context_count || 0} past interactions
                            </p>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Memory Tab */}
          <TabsContent value="memory" className="space-y-6">
            <Card className="border-2 shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-green-600" />
                  Memory Management
                </CardTitle>
                <CardDescription>
                  Explore Cognee's four memory lifecycle operations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">1. Remember</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Automatically stores every emotional interaction with rich context
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">2. Recall</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Retrieves relevant past contexts using semantic search
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">3. Improve</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Builds knowledge graph connections between memories
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">4. Forget</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Removes data when needed (GDPR compliant)
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* About Tab */}
          <TabsContent value="about" className="space-y-6">
            <Card className="border-2 shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-yellow-600" />
                  About EmoMemory
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="prose dark:prose-invert max-w-none">
                  <h3 className="text-xl font-semibold">The Problem</h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Traditional LLMs and AI systems are <strong>stateless</strong>. Every request starts from scratch:
                  </p>
                  <ul className="list-disc list-inside text-gray-600 dark:text-gray-400 space-y-1">
                    <li>No memory of past conversations</li>
                    <li>Context window limits (tokens run out)</li>
                    <li>Can't learn from user patterns</li>
                    <li>Forgets important emotional context</li>
                  </ul>

                  <h3 className="text-xl font-semibold mt-6">The Solution: Cognee Memory</h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    <strong>EmoMemory</strong> uses Cognee to give emotion AI a permanent, hybrid graph-vector memory layer:
                  </p>
                  <div className="grid md:grid-cols-2 gap-4 mt-4">
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <h4 className="font-semibold text-blue-600 dark:text-blue-400">Remember</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Store emotional interactions persistently</p>
                    </div>
                    <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <h4 className="font-semibold text-purple-600 dark:text-purple-400">Recall</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Retrieve relevant past contexts</p>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <h4 className="font-semibold text-green-600 dark:text-green-400">Improve</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Build knowledge graph connections</p>
                    </div>
                    <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                      <h4 className="font-semibold text-red-600 dark:text-red-400">Forget</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Remove data (GDPR compliant)</p>
                    </div>
                  </div>

                  <h3 className="text-xl font-semibold mt-6">Built For</h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    WeMakeDevs x Cognee Hackathon 2025
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Powered by Cognee • Built with Next.js & FastAPI
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </main>
  )
}
