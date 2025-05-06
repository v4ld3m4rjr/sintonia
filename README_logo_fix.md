# Instruções para Personalizar a Logomarca

O arquivo `app.py` foi atualizado para:

1. Suprimir as mensagens de aviso do Streamlit
2. Usar uma imagem de exemplo do Imgur

## Para usar sua própria imagem:

1. Faça upload da sua imagem para um serviço como Imgur:
   - Acesse https://imgur.com/upload
   - Faça upload da sua imagem
   - Clique com o botão direito na imagem e selecione "Copiar endereço da imagem"

2. No arquivo `app.py`, localize a função `add_logo()` (aproximadamente linha 40) e substitua a URL:

```python
def add_logo():
    # URL direta da imagem
    logo_url = "https://i.imgur.com/UQgJ5Xt.png"  # Substitua esta URL pela URL da sua imagem

    # Resto da função...
```

3. Atualize seu repositório GitHub e reimplante no Render

## Dicas para resolver problemas com imagens:

- Certifique-se de que a URL da imagem é direta (geralmente termina com .png, .jpg, etc.)
- Verifique se a imagem é acessível publicamente (teste a URL em uma janela anônima do navegador)
- Use serviços confiáveis como Imgur, Cloudinary ou GitHub para hospedar a imagem
- Mantenha o tamanho da imagem razoável (menos de 1MB) para carregamento rápido
