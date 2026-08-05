import { render, screen } from '@testing-library/react';
import WhyWorthGrid from './WhyWorthGrid';

describe('WhyWorthGrid', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows placeholder UI while loading', () => {
    global.fetch = vi.fn(() => new Promise(() => {}));

    render(<WhyWorthGrid />);

    expect(screen.getByRole('region', { name: 'Чому варто' })).toHaveAttribute('aria-busy', 'true');
    expect(screen.getAllByRole('listitem')).toHaveLength(4);
  });

  it('renders blocks from API and keeps them keyboard focusable', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        why_worth: [
          { title: 'Прямий зв\'язок з виробниками', desc: 'Опис 1' },
          { title: 'Ексклюзивні пропозиції', desc: 'Опис 2' },
          { title: 'Інновації та тренди', desc: 'Опис 3' },
          { title: 'Співпраця та синергія', desc: 'Опис 4' },
        ],
      }),
    });

    render(<WhyWorthGrid />);

    const heading = await screen.findByText('Прямий зв\'язок з виробниками');
    expect(heading).toBeInTheDocument();
    const block = heading.closest('[role="listitem"]');
    expect(block).toHaveAttribute('tabindex', '0');
    expect(block).toHaveAttribute('aria-label', 'Прямий зв\'язок з виробниками');
    expect(screen.getByText('Опис 4')).toBeInTheDocument();
  });

  it('falls back to mock blocks when API data is unavailable', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    render(<WhyWorthGrid />);

    expect(await screen.findByText("Прямий зв'язок з виробниками")).toBeInTheDocument();
    expect(screen.getByText('Інновації та тренди')).toBeInTheDocument();
  });
});