import  StartupsGrid  from "../components/StartupsGrid"
import CTASection from "../components/CTASection"
import ForWhomGrid from "../components/ForWhomGrid"
import Hero from "../components/Hero/Hero"
import WhyWorthGrid from "../components/WhyWorthGrid"
import Footer from "../components/Footer"
import "./Home.css"

function Home() {
  return (
    <>
      <main className="landing-page">
        <Hero />
        <StartupsGrid />
        <CTASection />
        <ForWhomGrid />
        <WhyWorthGrid />
      </main>

      <Footer />
    </>
  )
}

export default Home;