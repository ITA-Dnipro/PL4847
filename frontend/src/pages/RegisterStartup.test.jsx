import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import RegisterStartup from './RegisterStartup'

function mockFooterFetch(url) {
  if (url === '/api/content/landing/') {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: async () => ({ footer_links: { left: [], right: [] } }),
    })
  }
  return Promise.resolve({ ok: false, status: 404, json: async () => ({}) })
}

function registerCalls() {
  return global.fetch.mock.calls.filter(([url]) => url === '/api/auth/register/')
}

function renderForm() {
  return render(
    <MemoryRouter>
      <RegisterStartup />
    </MemoryRouter>
  )
}

function fillValidForm() {
  fireEvent.change(screen.getByLabelText('Електронна пошта'), { target: { value: 'alice@example.com' } })
  fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'StrongPass123' } })
  fireEvent.change(screen.getByLabelText('Повторіть пароль'), { target: { value: 'StrongPass123' } })
  fireEvent.change(screen.getByLabelText("Ім'я"), { target: { value: 'Alice' } })
  fireEvent.change(screen.getByLabelText('Прізвище'), { target: { value: 'Smith' } })
  fireEvent.change(screen.getByLabelText('Назва компанії'), { target: { value: 'Handmade Co' } })
  fireEvent.click(screen.getByLabelText('Я погоджуюсь з умовами використання'))
}

describe('RegisterStartup', () => {
  beforeEach(() => {
    global.fetch = vi.fn(mockFooterFetch)
  })

  it('renders the required fields', () => {
    renderForm()
    expect(screen.getByLabelText('Електронна пошта')).toBeInTheDocument()
    expect(screen.getByLabelText('Пароль')).toBeInTheDocument()
    expect(screen.getByLabelText('Назва компанії')).toBeInTheDocument()
    expect(screen.getByLabelText('Я погоджуюсь з умовами використання')).toBeInTheDocument()
  })

  it('renders a link to log in for people who already have an account', () => {
    renderForm()
    const link = screen.getByRole('link', { name: 'Увійти' })
    expect(link).toHaveAttribute('href', '/login')
  })

  it('shows validation errors and does not call the register API when submitted blank', () => {
    renderForm()
    fireEvent.click(screen.getByRole('button', { name: 'Зареєструватися' }))

    expect(screen.getByText('Не ввели електронну пошту')).toBeInTheDocument()
    expect(screen.getByText('Не ввели пароль')).toBeInTheDocument()
    expect(screen.getByText('Потрібно погодитися з умовами використання')).toBeInTheDocument()
    expect(registerCalls()).toHaveLength(0)
  })

  it('blocks submit when terms are not accepted, even if everything else is valid', () => {
    renderForm()
    fireEvent.change(screen.getByLabelText('Електронна пошта'), { target: { value: 'alice@example.com' } })
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'StrongPass123' } })
    fireEvent.change(screen.getByLabelText('Повторіть пароль'), { target: { value: 'StrongPass123' } })
    fireEvent.change(screen.getByLabelText("Ім'я"), { target: { value: 'Alice' } })
    fireEvent.change(screen.getByLabelText('Прізвище'), { target: { value: 'Smith' } })
    fireEvent.change(screen.getByLabelText('Назва компанії'), { target: { value: 'Handmade Co' } })

    fireEvent.click(screen.getByRole('button', { name: 'Зареєструватися' }))

    expect(screen.getByText('Потрібно погодитися з умовами використання')).toBeInTheDocument()
    expect(registerCalls()).toHaveLength(0)
  })

  it('shows a mismatch error when passwords do not match', () => {
    renderForm()
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'StrongPass123' } })
    fireEvent.change(screen.getByLabelText('Повторіть пароль'), { target: { value: 'Different123' } })
    fireEvent.click(screen.getByRole('button', { name: 'Зареєструватися' }))

    expect(screen.getByText('Паролі не збігаються')).toBeInTheDocument()
  })

  it('shows the selected filename and rejects an invalid file type', () => {
    renderForm()
    const badFile = new File(['not a pdf'], 'notes.txt', { type: 'text/plain' })
    fireEvent.change(screen.getByLabelText('Презентація або логотип'), { target: { files: [badFile] } })

    expect(screen.getByText('Обраний файл: notes.txt')).toBeInTheDocument()

    fillValidForm()
    fireEvent.click(screen.getByRole('button', { name: 'Зареєструватися' }))

    expect(screen.getByText('Файл має бути у форматі PDF, PNG або JPG')).toBeInTheDocument()
  })

  it('submits to the API and shows the confirmation on success', async () => {
    global.fetch.mockImplementation((url) => {
      if (url === '/api/auth/register/') {
        return Promise.resolve({
          ok: true,
          status: 201,
          json: async () => ({ id: 1, email: 'alice@example.com', detail: 'Verification email sent.' }),
        })
      }
      return mockFooterFetch(url)
    })

    renderForm()
    fillValidForm()
    fireEvent.click(screen.getByRole('button', { name: 'Зареєструватися' }))

    await waitFor(() => {
        expect(screen.getByText(/відправлено листа/i)).toBeInTheDocument()
      })


    const calls = registerCalls()
    expect(calls).toHaveLength(1)
    expect(calls[0][1]).toEqual(expect.objectContaining({ method: 'POST' }))

    const sentBody = JSON.parse(calls[0][1].body)
    expect(sentBody.role).toBe('startup')
    expect(sentBody.pitch_deck).toBeUndefined()
  })

  it('displays field errors returned by the server', async () => {
    global.fetch.mockImplementation((url) => {
      if (url === '/api/auth/register/') {
        return Promise.resolve({
          ok: false,
          status: 400,
          json: async () => ({ email: ['A user with this email already exists'] }),
        })
      }
      return mockFooterFetch(url)
    })

    renderForm()
    fillValidForm()
    fireEvent.click(screen.getByRole('button', { name: 'Зареєструватися' }))

    await waitFor(() => {
      expect(screen.getByText('A user with this email already exists')).toBeInTheDocument()
    })
  })
})
