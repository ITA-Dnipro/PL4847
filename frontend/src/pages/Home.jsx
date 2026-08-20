import  StartupsGrid  from "../components/StartupsGrid"
import CTASection from "../components/CTASection"
import ForWhomGrid from "../components/ForWhomGrid"
import Hero from "../components/Hero/Hero"
import WhyWorthGrid from "../components/WhyWorthGrid"
import Footer from "../components/Footer"

function Home() {
  return (
    <div>
      <Hero />
      <StartupsGrid />
      <CTASection />
      <ForWhomGrid />
      <WhyWorthGrid />
      <Footer />
    </div>
)
}

export default Home;