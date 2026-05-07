pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.11'
        VENV_DIR       = '.venv'
        ALLURE_RESULTS = 'allure-results'
        TEST_EMAIL     = credentials('notes-test-email')
        TEST_PASSWORD  = credentials('notes-test-password')
        HEADLESS       = 'true'
        BROWSER        = 'chrome'
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Checkout complete — branch: ${env.GIT_BRANCH}"
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python${PYTHON_VERSION} -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint & Static Analysis') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pip install flake8 --quiet
                    flake8 pages/ api_client/ utils/ tests/ \
                        --max-line-length=100 \
                        --ignore=E501,W503 \
                        --exclude=__pycache__ || true
                '''
            }
        }

        stage('Run Tests — Parallel') {
            parallel {

                stage('UI Tests') {
                    steps {
                        sh '''
                            . ${VENV_DIR}/bin/activate
                            pytest tests/ui \
                                -m ui \
                                -n 2 \
                                --alluredir=${ALLURE_RESULTS} \
                                --tb=short \
                                -v \
                                --reruns=2 \
                                --reruns-delay=1 \
                                -o "markers=ui"
                        '''
                    }
                }

                stage('API Tests') {
                    steps {
                        sh '''
                            . ${VENV_DIR}/bin/activate
                            pytest tests/api \
                                -m api \
                                -n 3 \
                                --alluredir=${ALLURE_RESULTS} \
                                --tb=short \
                                -v
                        '''
                    }
                }

            }
        }

        stage('Run E2E Hybrid Tests') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest tests/e2e \
                        -m e2e \
                        -n 1 \
                        --alluredir=${ALLURE_RESULTS} \
                        --tb=long \
                        -v
                '''
            }
        }

        stage('Generate Allure Report') {
            steps {
                allure([
                    includeProperties: false,
                    jdk:               '',
                    properties:        [],
                    reportBuildPolicy: 'ALWAYS',
                    results:           [[path: "${ALLURE_RESULTS}"]]
                ])
            }
        }

    }

    post {
        always {
            archiveArtifacts artifacts: 'screenshots/**/*.png, logs/**/*.log, allure-results/**', allowEmptyArchive: true
            echo "📦 Artifacts archived"
        }
        success {
            echo "✅ All tests PASSED"
        }
        failure {
            echo "❌ Build FAILED — check Allure report for details"
            emailext(
                subject: "❌ Notes Automation FAILED — Build #${env.BUILD_NUMBER}",
                body: "Check: ${env.BUILD_URL}",
                to: "${env.TEST_EMAIL}"
            )
        }
        unstable {
            echo "⚠️ Build UNSTABLE — some tests failed"
        }
    }
}
