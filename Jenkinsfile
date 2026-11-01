pipeline {
    agent any

    options {
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    environment {
        IMAGE_NAME = 'innotwist/devops-health-checker'
        APP_PORT   = '5000'
        // Tag unique : numéro de build + 7 premiers caractères du commit Git
        IMAGE_TAG  = "${env.BUILD_NUMBER}-${env.GIT_COMMIT ? env.GIT_COMMIT.take(7) : 'local'}"
    }

    stages {

        // ── Stage 1 : Récupération du code source ──────────────────────────
        stage('1. Checkout SCM') {
            steps {
                echo '📥 Récupération du code source depuis GitHub...'
                checkout scm
                sh 'echo "Commit: $(git rev-parse --short HEAD 2>/dev/null || echo local)"'
                sh 'ls -la'
            }
        }

        // ── Stage 2 : Analyse statique du code (Linting) ──────────────────
        stage('2. Code Quality — Flake8') {
            steps {
                echo '🔍 Analyse statique du code avec flake8...'
                sh 'python3 -m pip install --quiet --break-system-packages flake8'
                sh 'python3 -m flake8 app.py --max-line-length=100 --ignore=E501,W503'
                echo '✅ Analyse flake8 terminée — aucune erreur critique détectée.'
            }
        }

        // ── Stage 3 : Tests unitaires automatisés ─────────────────────────
        stage('3. Unit Tests — Pytest') {
            steps {
                echo '🧪 Installation des dépendances de test...'
                sh 'python3 -m pip install --quiet --break-system-packages -r requirements.txt'
                sh 'python3 -m pip install --quiet --break-system-packages -r requirements-dev.txt'
                echo '🧪 Exécution de la suite de tests pytest...'
                sh 'mkdir -p reports'
                sh 'python3 -m pytest test_app.py -v --junitxml=reports/test-results.xml --tb=short'
            }
            post {
                always {
                    // Publier les résultats de tests dans Jenkins (nécessite le plugin JUnit)
                    junit allowEmptyResults: true, testResults: 'reports/*.xml'
                    echo '📊 Rapport de tests publié dans Jenkins.'
                }
            }
        }

        // ── Stage 4 : Construction de l'image Docker ──────────────────────
        stage('4. Docker Build & Tag') {
            steps {
                echo "🐳 Construction de l'image Docker : ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest"
                echo '✅ Image construite et taguée avec succès.'
            }
        }

        // ── Stage 5 : Inspection de sécurité de l'image ──────────────────
        stage('5. Image Inspection') {
            steps {
                echo '🔒 Inspection de la taille et des couches de l\'image Docker...'
                sh "docker images ${IMAGE_NAME} --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}'"
                sh "docker history ${IMAGE_NAME}:${IMAGE_TAG} --no-trunc=false"
            }
        }

        // ── Stage 6 : Déploiement en environnement Staging ────────────────
        stage('6. Deploy — Staging') {
            steps {
                echo '🚀 Déploiement du conteneur en Staging...'
                // Nettoyage de l'éventuel conteneur précédent
                sh 'docker stop staging-health-app || true'
                sh 'docker rm   staging-health-app || true'
                // Lancement du nouveau conteneur
                sh """docker run -d \
                    --name staging-health-app \
                    -p ${APP_PORT}:5000 \
                    -e APP_ENV=staging \
                    -e APP_VERSION=${IMAGE_TAG} \
                    --restart unless-stopped \
                    ${IMAGE_NAME}:${IMAGE_TAG}"""
                // Attendre que l'app soit prête
                sh 'sleep 5'
                echo '🏥 Vérification du Health Check...'
                sh "curl -f http://localhost:${APP_PORT}/health || (docker logs staging-health-app && exit 1)"
                sh "curl -s http://localhost:${APP_PORT}/api/info | python3 -m json.tool"
                echo '✅ Application déployée et healthy en Staging !'
            }
        }

    }

    post {
        success {
            echo '''
╔══════════════════════════════════════════════════════╗
║   ✅  PIPELINE SUCCÈS — DevOps Health Checker        ║
║   Toutes les étapes sont passées au vert !           ║
╚══════════════════════════════════════════════════════╝'''
        }
        failure {
            echo '''
╔══════════════════════════════════════════════════════╗
║   ❌  PIPELINE ÉCHEC — Vérifiez les logs ci-dessus  ║
╚══════════════════════════════════════════════════════╝'''
            // Nettoyage en cas d'échec
            sh 'docker stop staging-health-app || true'
            sh 'docker rm   staging-health-app || true'
        }
        always {
            echo '🧹 Nettoyage de l\'espace de travail Jenkins...'
            cleanWs deleteDirs: true, notFailBuild: true
        }
    }
}
