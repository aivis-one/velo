// =============================================================================
// VELO Frontend — Mock Messages Data (S2-S3 SPEEDRUN MEGA-2 §C49)
//
// Static mock conversations + threads. Real backend wiring deferred per
// BACKEND-COORDINATION § A.7 Messages mock.
// =============================================================================

export type Counterparty = {
  id: string
  name: string
  avatar_url: string | null
  role: 'master' | 'support'
}

export type ConversationMessage = {
  id: string
  sender_id: string
  text: string
  created_at: string
  is_read: boolean
}

export type Conversation = {
  id: string
  counterparty: Counterparty
  last_message: { text: string; created_at: string; is_unread: boolean }
  unread_count: number
}

export const MOCK_CONVERSATIONS: Conversation[] = [
  {
    id: 'conv-1',
    counterparty: {
      id: 'master-alex-mindful',
      name: 'Alex Mindful',
      avatar_url: '/assets/masters/alex-mindful.svg',
      role: 'master',
    },
    last_message: {
      text: 'Конечно, эта практика подходит для начинающих! Она специально разработана для мягкого входа в медитацию',
      created_at: '2026-01-25T12:15:00Z',
      is_unread: true,
    },
    unread_count: 1,
  },
  {
    id: 'conv-2',
    counterparty: {
      id: 'support',
      name: 'Поддержка VELΘ',
      avatar_url: null,
      role: 'support',
    },
    last_message: {
      text: 'Здравствуйте! Ваш вопрос решен. Если проблема повторится, пожалуйста, напишите нам снова.',
      created_at: '2026-01-24T12:15:00Z',
      is_unread: false,
    },
    unread_count: 0,
  },
  {
    id: 'conv-3',
    counterparty: {
      id: 'master-maria-flow',
      name: 'Maria Flow',
      avatar_url: '/assets/masters/maria-flow.svg',
      role: 'master',
    },
    last_message: {
      text: 'Рада, что вам понравилось!',
      created_at: '2026-01-23T10:00:00Z',
      is_unread: false,
    },
    unread_count: 0,
  },
]

export const MOCK_THREADS: Record<string, ConversationMessage[]> = {
  'conv-1': [
    {
      id: 'm-1-1',
      sender_id: 'me',
      text: 'Подходит ли эта практика для начинающих?',
      created_at: '2026-01-25T12:10:00Z',
      is_read: true,
    },
    {
      id: 'm-1-2',
      sender_id: 'master-alex-mindful',
      text: 'Конечно, эта практика подходит для начинающих! Она специально разработана для мягкого входа в медитацию',
      created_at: '2026-01-25T12:15:00Z',
      is_read: false,
    },
  ],
  'conv-2': [
    {
      id: 'm-2-1',
      sender_id: 'me',
      text: 'У меня не работает оплата',
      created_at: '2026-01-24T12:10:00Z',
      is_read: true,
    },
    {
      id: 'm-2-2',
      sender_id: 'support',
      text: 'Здравствуйте! Ваш вопрос решен. Если проблема повторится, пожалуйста, напишите нам снова.',
      created_at: '2026-01-24T12:15:00Z',
      is_read: false,
    },
  ],
  'conv-3': [
    {
      id: 'm-3-1',
      sender_id: 'me',
      text: 'Спасибо за практику!',
      created_at: '2026-01-23T09:30:00Z',
      is_read: true,
    },
    {
      id: 'm-3-2',
      sender_id: 'master-maria-flow',
      text: 'Рада, что вам понравилось!',
      created_at: '2026-01-23T10:00:00Z',
      is_read: true,
    },
  ],
}
