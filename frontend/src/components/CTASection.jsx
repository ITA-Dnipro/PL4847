import "./CTASection.css"

function CTASection({
  title = "Майданчик для тих, хто втілює свої ідеї в життя",
  buttonText = "Долучитися",
  onButtonClick,
}) {
  return (
    <section className="cta-section">
      <div className="cta-section__inner">
        <h2 className="cta-section__title">{title}</h2>
        <button className="cta-section__button" onClick={onButtonClick}>
          {buttonText}
        </button>
      </div>
    </section>
  )
}

export default CTASection