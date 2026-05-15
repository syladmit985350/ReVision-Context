#!/usr/bin/env bash
set -eu

mkdir -p third_party

clone_if_missing() {
  repo_url="$1"
  target_dir="$2"

  if [ ! -d "$target_dir" ]; then
    git clone "$repo_url" "$target_dir"
  else
    echo "Skipping existing $target_dir"
  fi
}

clone_if_missing "https://github.com/CSU-JPG/VIST.git" "third_party/VIST"
clone_if_missing "https://github.com/thu-coai/Glyph.git" "third_party/Glyph"
clone_if_missing "https://github.com/princeton-nlp/CEPE.git" "third_party/CEPE"
clone_if_missing "https://github.com/yanhong-lbh/text_or_pixels.git" "third_party/text_or_pixels"
clone_if_missing "https://github.com/deepseek-ai/DeepSeek-OCR.git" "third_party/DeepSeek-OCR"
clone_if_missing "https://github.com/liufanfanlff/C3-Context-Cascade-Compression.git" "third_party/C3-Context-Cascade-Compression"
clone_if_missing "https://github.com/YerbaPage/LongCodeZip.git" "third_party/LongCodeZip"
clone_if_missing "https://github.com/microsoft/LLMLingua.git" "third_party/LLMLingua"
clone_if_missing "https://github.com/liyucheng09/Selective_Context.git" "third_party/Selective_Context"
clone_if_missing "https://github.com/Beckschen/LLaVolta.git" "third_party/LLaVolta"
