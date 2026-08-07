import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import mockLanding from "../../data/landing.json"
import "./Hero.css"


function Hero() {
  const mockHero = mockLanding.hero ?? mockLanding
  const [hero, setHero] = useState(mockHero)

  useEffect(() => {
    async function loadHero() {
      try {
        const response = await fetch("/api/content/landing/")

        if (!response.ok) {
          throw new Error("Failed to load hero content")
        }

        const data = await response.json()

        if (!data.hero) {
          throw new Error("Hero content is missing")
        }

        setHero({
          title: data.hero.title,
          subtitle: data.hero.subtitle,
          ctaText: data.hero.cta_text,
          ctaLink: "/register",
          images:
            data.hero.hero_images?.length > 0
              ? data.hero.hero_images
              : mockHero.images,
        })
      } catch {
        setHero(mockHero)
      }
    }

    loadHero()
  }, [mockHero])

  if (!hero) {
    return null
  }

  return (
    <section className="hero">
      <div className="hero__content">
        <h1>{hero.title}</h1>
        <p>{hero.subtitle}</p>

        <Link className="hero__cta" to={hero.ctaLink || "/register"}>
          {hero.ctaText}
        </Link>
      </div>

      <div className="hero__collage">
        {(hero.images || []).map((image, index) => (
          <img
            key={image.src || index}
            src={image.src || image}
            alt={image.alt || `Hero image ${index + 1}`}
            loading="lazy"
          />
        ))}
      </div>
    </section>
  )
}

export default Hero