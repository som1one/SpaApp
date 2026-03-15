from pathlib import Path

import cairosvg


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def render_android():
  """Конвертирует SVG логотип в PNG для Android splash."""
  svg_path = PROJECT_ROOT / "assets" / "images" / "logo_priroda.svg"
  out_dir = PROJECT_ROOT / "android" / "app" / "src" / "main" / "res" / "drawable"
  out_dir.mkdir(parents=True, exist_ok=True)

  png_path = out_dir / "splash_priroda.png"

  # Высокое разрешение, чтобы на больших экранах было чётко.
  # Масштаб подбираем так, чтобы логотип занимал большую часть по высоте,
  # как на оригинальной картинке.
  cairosvg.svg2png(
    url=str(svg_path),
    write_to=str(png_path),
    output_width=1080,
    output_height=1920,
    background_color="white",
  )


def render_ios():
  """Конвертирует SVG логотип в PNG для iOS LaunchImage (1x, 2x, 3x)."""
  svg_path = PROJECT_ROOT / "assets" / "images" / "logo_priroda.svg"
  out_dir = PROJECT_ROOT / "ios" / "Runner" / "Assets.xcassets" / "LaunchImage.imageset"
  out_dir.mkdir(parents=True, exist_ok=True)

  sizes = [
    (1080, 1920, "LaunchImage.png"),
    (2160, 3840, "LaunchImage@2x.png"),
    (3240, 5760, "LaunchImage@3x.png"),
  ]

  for width, height, name in sizes:
    cairosvg.svg2png(
      url=str(svg_path),
      write_to=str(out_dir / name),
      output_width=width,
      output_height=height,
      background_color="white",
    )


def main():
  render_android()
  render_ios()


if __name__ == "__main__":
  main()


