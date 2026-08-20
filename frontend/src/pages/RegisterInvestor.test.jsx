import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import RegisterInvestor from './RegisterInvestor'

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
      <RegisterInvestor />
    </MemoryRouter>
  )
}

function fillValidForm() {
  fireEvent.change(screen.getByLabelText('Назва інвестора або фонду'), { target: { value: 'Acme Capital' } })
  fireEvent.click(screen.getByLabelText('Індивідуальний інвестор'))
  fireEvent.change(screen.getByLabelText('Електронна пошта'), { target: { value: 'alice@example.com' } })
  fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'StrongPass123' } })
  fireEvent.change(screen.getByLabelText('Повторіть пароль'), { target: { value: 'StrongPass123' } })
  fireEvent.change(screen.getByLabelText("Ім'я"), { target: { value: 'Alice' } })
  fireEvent.change(screen.getByLabelText('Прізвище'), { target: { value: 'Smith' } })
  fireEvent.click(screen.getByLabelText(/Я погоджуюсь з/))
}

describe('RegisterInvestor', () => {
  beforeEach(() => {
    global.fetch = vi.fn(mockFooterFetch)
  })

  it('renders the required fields', () => {
    renderForm()
    expect(screen.getByLabelText('Назва інвестора або фонду')).toBeInTheDocument()
    expect(screen.getByLabelText('Індивідуальний інвестор')).toBeInTheDocument()
    expect(screen.getByLabelText('Фонд')).toBeInTheDocument()
    expect(screen.getByLabelText('Електронна пошта')).toBeInTheDocument()
    expect(screen.getByLabelText('Пароль')).toBeInTheDocument()
    expect(screen.getByLabelText('Мінімальна сума інвестиції ($)')).toBeInTheDocument()
    expect(screen.getByText('Fintech')).toBeInTheDocument()
    expect(screen.getByLabelText('Про себе')).toBeInTheDocument()
    expect(screen.getByLabelText('Веб-сайт')).toBeInTheDocument()
    expect(screen.getByLabelText(/Я погоджуюсь з/)).toBeInTheDocument()
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
    expect(screen.getByText('Оберіть тип інвестора')).toBeInTheDocument()
    expect(screen.getByText('Потрібно погодитися з умовами використання')).toBeInTheDocument()
    expect(registerCalls()).toHaveLength(0)
  })

  it('blocks submit when terms are not accepted, even if everything else is valid', () => {
    renderForm()
    fireEvent.change(screen.getByLabelText('Назва інвестора або фонду'), { target: { value: 'Acme Capital' } })
    fireEvent.click(screen.getByLabelText('Індивідуальний інвестор'))
    fireEvent.change(screen.getByLabelText('Електронна пошта'), { target: { value: 'alice@example.com' } })
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'StrongPass123' } })
    fireEvent.change(screen.getByLabelText('Повторіть пароль'), { target: { value: 'StrongPass123' } })
    fireEvent.change(screen.getByLabelText("Ім'я"), { target: { value: 'Alice' } })
    fireEvent.change(screen.getByLabelText('Прізвище'), { target: { value: 'Smith' } })

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

  it('rejects a negative minimum investment', () => {
    renderForm()
    fireEvent.change(screen.getByLabelText('Мінімальна сума інвестиції ($)'), { target: { value: '-500' } })
    fillValidForm()
    fireEvent.click(screen.getByRole('button', { name: 'Зареєструватися' }))

    expect(screen.getByText('Введіть коректну суму (число, не менше 0)')).toBeInTheDocument()
    expect(registerCalls()).toHaveLength(0)
  })

  it('shows an error for a malformed website URL', () => {
    renderForm()
    fireEvent.change(screen.getByLabelText('Веб-сайт'), { target: { value: 'not-a-url' } })
    fillValidForm()
    fireEvent.click(screen.getByRole('button', { name: 'Зареєструватися' }))

    expect(screen.getByText('Введіть коректне посилання, що починається з http:// або https://')).toBeInTheDocument()
    expect(registerCalls()).toHaveLength(0)
  })

  it('lets sector tags be toggled on and off', () => {
    renderForm()
    const fintech = screen.getByLabelText('Fintech')
    expect(fintech).not.toBeChecked()
    fireEvent.click(fintech)
    expect(fintech).toBeChecked()
    fireEvent.click(fintech)
    expect(fintech).not.toBeChecked()
  })

  it('submits to the API with the investor role and omits unsupported fields', async () => {
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
    fireEvent.click(screen.getByLabelText('Fintech'))
    fireEvent.change(screen.getByLabelText('Мінімальна сума інвестиції ($)'), { target: { value: '10000' } })
    fireEvent.change(screen.getByLabelText('Про себе'), { target: { value: 'Seed-stage fintech fund' } })
    fireEvent.change(screen.getByLabelText('Веб-сайт'), { target: { value: 'https://acme.capital' } })
    fireEvent.click(screen.getByRole('button', { name: 'Зареєструватися' }))

    await waitFor(() => {
      expect(screen.getByText(/відправлено листа/i)).toBeInTheDocument()
    })

    const calls = registerCalls()
    expect(calls).toHaveLength(1)
    expect(calls[0][1]).toEqual(expect.objectContaining({ method: 'POST' }))

    const sentBody = JSON.parse(calls[0][1].body)
    expect(sentBody.role).toBe('investor')
    expect(sentBody.company_name).toBe('Acme Capital')
    expect(sentBody.short_pitch).toBe('Seed-stage fintech fund')
    expect(sentBody.website).toBe('https://acme.capital')
    expect(sentBody.investor_type).toBeUndefined()
    expect(sentBody.investment_focus).toBeUndefined()
    expect(sentBody.min_investment).toBeUndefined()
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
