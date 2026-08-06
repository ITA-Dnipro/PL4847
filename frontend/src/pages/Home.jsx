import  StartupsGrid  from "../components/StartupsGrid"
import CTASection from "../components/CTASection"
import ForWhomGrid from "../components/ForWhomGrid"
import WhyWorthGrid from "../components/WhyWorthGrid"

function Home() {
  return (
    <div>
      <h1>Home page</h1>
      <StartupsGrid />
      <CTASection />
      <ForWhomGrid />
      <WhyWorthGrid />
    </div>
)
}

export default Home;