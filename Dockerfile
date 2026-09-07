# syntax=docker/dockerfile:1

# --- build : régénère site/resultats/ depuis les .md / .json versionnés ---
FROM python:3.12-alpine AS build
WORKDIR /app
RUN pip install --no-cache-dir pyyaml
COPY benchmark/ benchmark/
COPY resultats/ resultats/
COPY models.lock .
RUN python3 benchmark/build_pages.py

# --- run : nginx statique ---
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/site/resultats/ /usr/share/nginx/html/
EXPOSE 80
