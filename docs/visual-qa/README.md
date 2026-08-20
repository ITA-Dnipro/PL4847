# Desktop Landing Page Visual QA

## Environment

- Desktop
- Chrome
- Firefox
- Resolution: 1920x1080

## Visual review

### Hero
- Status: Passed
- Hero title, subtitle, CTA button and image collage are displayed correctly.

### Startup cards
- Status: Passed
- 8 startup cards are displayed on the landing page.
- Layout is displayed correctly on desktop.

### CTA section
- Status: Passed
- Section is displayed on the landing page.

### For whom section
- Status: Passed
- Section is displayed on the landing page.

### Why worth section
- Status: Passed
- Section is displayed on the landing page.

## Cross-browser

- Chrome: Passed
- Firefox: Passed

## Lighthouse

- Performance: 66
- Accessibility: 100

## Automated checks

- ESLint: Passed
- Unit tests: 14/14 passed
- Production build: Passed
- Playwright Chromium: Passed
- Playwright Firefox: Passed
- E2E smoke test: Hero and 8 startup cards passed

## Accessibility fixes

- Added the main page landmark.
- Fixed low-contrast text.
- Improved contrast for Header buttons.
- Improved contrast for the startup section link.

## Screenshots

- [Chrome landing page](./landing-chrome.png)
- [Firefox landing page](./landing-firefox.png)
- [Lighthouse desktop report](./lighthouse-desktop.png)

## Notes

- Lighthouse desktop check completed with Performance 66 and Accessibility 100.
- The local backend was unavailable during part of the QA, so frontend fallback data was used.
- Lighthouse performance results may vary between runs.