import { expect, test } from "@playwright/test"

test("landing page shows hero and 8 startup cards", async ({ page }) => {
  const startups = Array.from({ length: 8 }, (_, index) => ({
    id: index + 1,
    company_name: `API Startup ${index + 1}`,
    short_description: `Startup description ${index + 1}`,
    location: "Kyiv",
    tags: ["Test"],
    thumbnail_url: "https://placehold.co/300x200",
  }))

  await page.route("**/api/startups/**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        count: 8,
        next: null,
        previous: null,
        results: startups,
      }),
    })
  })

  await page.goto("/")

  const heroTitle = page.locator(".hero h1")

  await expect(heroTitle).toBeVisible()
  await expect(heroTitle).not.toHaveText("")

  await expect(
    page.getByRole("heading", { name: "Нові учасники" })
  ).toBeVisible()

  await expect(page.getByText("API Startup 1")).toBeVisible()
  await expect(page.locator(".startup-card")).toHaveCount(8)
})