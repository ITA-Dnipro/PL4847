import  StartupsGrid  from "../components/StartupsGrid"
import CTASection from "../components/CTASection"
import ForWhomGrid from "../components/ForWhomGrid"

function Home() {
  return (
    <div>
      <h1>Home page</h1>
      <StartupsGrid />
      <CTASection />
      <ForWhomGrid />
    </div>
);
}

export default Home;