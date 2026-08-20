import { useState } from "react"
import { Link } from "react-router-dom"
import Footer from "../components/Footer"
import "./RegisterStartup.css"

const ALLOWED_FILE_TYPES = ["application/pdf", "image/png", "image/jpeg"]
const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024 // 5MB

function RegisterStartup() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    password_confirm: "",
    first_name: "",
    last_name: "",
    company_name: "",
    short_pitch: "",
    website: "",
    contact_phone: "",
    pitch_deck: null,
    terms_accepted: false,
  })

  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [serverError, setServerError] = useState("")
  const [submitted, setSubmitted] = useState(false)
  const [resending, setResending] = useState(false)
  const [resendMessage, setResendMessage] = useState("")

  function handleChange(e) {
    const { name, value, type, checked, files } = e.target

    if (type === "checkbox") {
      setFormData({ ...formData, [name]: checked })
    } else if (type === "file") {
      setFormData({ ...formData, [name]: files[0] })
    } else if (name === "contact_phone") {
      const digitsOnly = value.replace(/\D/g, "").slice(0, 9)
      setFormData({ ...formData, contact_phone: digitsOnly })
    } else {
      setFormData({ ...formData, [name]: value })
    }
  }

  function validate() {
    const newErrors = {}

    if (!formData.email) {
      newErrors.email = "Не ввели електронну пошту"
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Введіть коректну електронну пошту"
    }

    if (!formData.password) {
      newErrors.password = "Не ввели пароль"
    } else if (formData.password.length < 8) {
      newErrors.password = "Пароль має містити щонайменше 8 символів"
    }

    if (!formData.password_confirm) {
      newErrors.password_confirm = "Не ввели пароль ще раз"
    } else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = "Паролі не збігаються"
    }

    if (!formData.first_name) {
      newErrors.first_name = "Не ввели ім'я"
    }

    if (!formData.last_name) {
      newErrors.last_name = "Не ввели прізвище"
    }

    if (!formData.company_name) {
      newErrors.company_name = "Не ввели назву компанії"
    }

    if (formData.website && !/^https?:\/\/.+/.test(formData.website)) {
      newErrors.website = "Введіть коректне посилання, що починається з http:// або https://"
    }

    if (formData.pitch_deck) {
      if (!ALLOWED_FILE_TYPES.includes(formData.pitch_deck.type)) {
        newErrors.pitch_deck = "Файл має бути у форматі PDF, PNG або JPG"
      } else if (formData.pitch_deck.size > MAX_FILE_SIZE_BYTES) {
        newErrors.pitch_deck = "Розмір файлу не повинен перевищувати 5МБ"
      }
    }

    if (!formData.terms_accepted) {
      newErrors.terms_accepted = "Потрібно погодитися з умовами використання"
    }

    return newErrors
  }

  async function handleSubmit(e) {
    e.preventDefault()

    const validationErrors = validate()
    setErrors(validationErrors)

    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setServerError("")
    setIsSubmitting(true)

    try {
      const response = await fetch("/api/auth/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          password_confirm: formData.password_confirm,
          first_name: formData.first_name,
          last_name: formData.last_name,
          company_name: formData.company_name,
          role: "startup",
          short_pitch: formData.short_pitch,
          website: formData.website,
          contact_phone: formData.contact_phone ? `+380${formData.contact_phone}` : "",
        }),
      })

      const data = await response.json()

      if (response.status === 201) {
        setSubmitted(true)
      } else if (response.status === 400) {
        const fieldErrors = {}
        for (const field in data) {
          fieldErrors[field] = Array.isArray(data[field]) ? data[field][0] : data[field]
        }
        setErrors(fieldErrors)
      } else if (response.status === 409) {
        setErrors({ email: data.detail })
      } else {
        setServerError("Щось пішло не так. Спробуйте ще раз.")
      }
    } catch {
      setServerError("Не вдалося з'єднатися із сервером. Перевірте підключення та спробуйте ще раз.")
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleResend() {
    setResending(true)
    setResendMessage("")

    try {
      await fetch("/api/auth/resend-verification/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: formData.email }),
      })
    } finally {
      // The endpoint always responds the same way regardless of outcome
      // (anti-enumeration by design), so there's nothing to branch on here.
      setResendMessage("Лист надіслано ще раз.")
      setResending(false)
    }
  }

  if (submitted) {
    return (
      <>
        <div className="register-startup">
          <div className="register-startup__card register-startup__card--confirmation" aria-live="polite">
            <div className="register-startup__confirmation-header">
              <h1 className="register-startup__title">Реєстрація майже завершена</h1>
            </div>

            <div className="register-startup__confirmation-body">
              <p>
                На вашу електронну пошту {formData.email} відправлено листа. Будь ласка,
                перейдіть за посиланням з листа для підтвердження вказаної електронної адреси.
              </p>

              <p className="register-startup__resend">
                Не отримали листа?{" "}
                <button
                  type="button"
                  className="register-startup__resend-link"
                  onClick={handleResend}
                  disabled={resending}
                >
                  Надіслати ще раз
                </button>
              </p>

              {resendMessage && <p className="register-startup__resend-message">{resendMessage}</p>}
            </div>

            <div className="register-startup__confirmation-footer">
              <Link to="/login" className="register-startup__submit">
                Повернутися до входу
              </Link>
            </div>
          </div>
        </div>
        <Footer />
      </>
    )
  }

  return (
    <>
      <div className="register-startup">
        <form className="register-startup__card" onSubmit={handleSubmit} noValidate>
          <h1 className="register-startup__title">Реєстрація стартапу</h1>

          <p className="register-startup__required-note">* Обов'язкові поля позначені зірочкою</p>

          {serverError && (
            <p className="register-startup__server-error" role="alert">
              {serverError}
            </p>
          )}

          <div className="register-startup__field">
            <span className="register-startup__label-row">
              <label className="register-startup__label" htmlFor="company_name">Назва компанії</label>
              <span className="register-startup__required-mark" aria-hidden="true">*</span>
            </span>
            <input className="register-startup__input" type="text" id="company_name" name="company_name" value={formData.company_name} onChange={handleChange} placeholder="Введіть назву компанії" />
            {errors.company_name && <p className="register-startup__error">{errors.company_name}</p>}
          </div>

          <div className="register-startup__field">
            <span className="register-startup__label-row">
              <label className="register-startup__label" htmlFor="email">Електронна пошта</label>
              <span className="register-startup__required-mark" aria-hidden="true">*</span>
            </span>
            <input className="register-startup__input" type="email" id="email" name="email" value={formData.email} onChange={handleChange} placeholder="Введіть свою електронну пошту" />
            {errors.email && <p className="register-startup__error">{errors.email}</p>}
          </div>

          <div className="register-startup__field">
            <span className="register-startup__label-row">
              <label className="register-startup__label" htmlFor="password">Пароль</label>
              <span className="register-startup__required-mark" aria-hidden="true">*</span>
            </span>
            <p className="register-startup__hint">
              Пароль повинен мати 8+ символів, містити принаймні велику, малу літеру (A..Z, a..z) та цифру (0..9).
            </p>
            <input className="register-startup__input" type="password" id="password" name="password" value={formData.password} onChange={handleChange} placeholder="Введіть пароль" />
            {errors.password && <p className="register-startup__error">{errors.password}</p>}
          </div>

          <div className="register-startup__field">
            <span className="register-startup__label-row">
              <label className="register-startup__label" htmlFor="password_confirm">Повторіть пароль</label>
              <span className="register-startup__required-mark" aria-hidden="true">*</span>
            </span>
            <input className="register-startup__input" type="password" id="password_confirm" name="password_confirm" value={formData.password_confirm} onChange={handleChange} placeholder="Введіть пароль ще раз" />
            {errors.password_confirm && <p className="register-startup__error">{errors.password_confirm}</p>}
          </div>

          <div className="register-startup__field">
            <span className="register-startup__label-row">
              <label className="register-startup__label" htmlFor="first_name">Ім'я</label>
              <span className="register-startup__required-mark" aria-hidden="true">*</span>
            </span>
            <input className="register-startup__input" type="text" id="first_name" name="first_name" value={formData.first_name} onChange={handleChange} placeholder="Введіть ваше ім'я" />
            {errors.first_name && <p className="register-startup__error">{errors.first_name}</p>}
          </div>

          <div className="register-startup__field">
            <span className="register-startup__label-row">
              <label className="register-startup__label" htmlFor="last_name">Прізвище</label>
              <span className="register-startup__required-mark" aria-hidden="true">*</span>
            </span>
            <input className="register-startup__input" type="text" id="last_name" name="last_name" value={formData.last_name} onChange={handleChange} placeholder="Введіть ваше прізвище" />
            {errors.last_name && <p className="register-startup__error">{errors.last_name}</p>}
          </div>

          <div className="register-startup__field">
            <label className="register-startup__label" htmlFor="short_pitch">Короткий пітч</label>
            <textarea className="register-startup__input" id="short_pitch" name="short_pitch" value={formData.short_pitch} onChange={handleChange} />
          </div>

          <div className="register-startup__field">
            <label className="register-startup__label" htmlFor="website">Веб-сайт</label>
            <input className="register-startup__input" type="url" id="website" name="website" value={formData.website} onChange={handleChange} />
            {errors.website && <p className="register-startup__error">{errors.website}</p>}
          </div>

          <div className="register-startup__field">
            <label className="register-startup__label" htmlFor="contact_phone">Контактний телефон</label>
            <div className="register-startup__phone">
              <span className="register-startup__phone-prefix">+380</span>
              <input
                className="register-startup__input register-startup__input--phone"
                type="tel"
                id="contact_phone"
                name="contact_phone"
                value={formData.contact_phone}
                onChange={handleChange}
                placeholder="XXXXXXXXX"
                maxLength={9}
              />
            </div>
          </div>

          <div className="register-startup__field">
            <label className="register-startup__label" htmlFor="pitch_deck">Презентація або логотип</label>
            <input
              className="register-startup__input register-startup__input--file"
              type="file"
              id="pitch_deck"
              name="pitch_deck"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleChange}
            />
            {formData.pitch_deck && <p className="register-startup__filename">Обраний файл: {formData.pitch_deck.name}</p>}
            {errors.pitch_deck && <p className="register-startup__error">{errors.pitch_deck}</p>}
          </div>

          <div className="register-startup__field register-startup__field--checkbox">
            <label className="register-startup__checkbox-label">
              <input className="register-startup__checkbox" type="checkbox" name="terms_accepted" checked={formData.terms_accepted} onChange={handleChange} />
              Я погоджуюсь з умовами використання
            </label>
            <span className="register-startup__required-mark" aria-hidden="true">*</span>
            {errors.terms_accepted && <p className="register-startup__error">{errors.terms_accepted}</p>}
          </div>

          <button className="register-startup__submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Реєстрація..." : "Зареєструватися"}
          </button>

          <p className="register-startup__login-hint">
            Ви вже зареєстровані?{" "}
            <Link to="/login" className="register-startup__login-link">
              <span className="register-startup__login-link-label">Увійти</span>
              <span className="register-startup__login-link-underline" />
            </Link>
          </p>
        </form>
      </div>
      <Footer />
    </>
  )
}

export default RegisterStartup
