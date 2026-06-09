export interface AuthResponse {
  access_token: string
  token_type: string
  user_id: string
  role: string
}

export interface Source {
  file: string
  page: number | string
  score: number
}

export interface ChatResponse {
  answer: string
  sources: Source[]
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
}
