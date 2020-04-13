pipeline {
    agent any
    stages {
        stage('Install miniconda') {
			steps {
				sh '''#!/usr/bin/env bash
				wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -nv -O miniconda.sh
				bash miniconda.sh -b -u -p $WORKSPACE/miniconda
				'''
			}
		}
		stage('Setup environment') {
			steps {
				sh '''#!/usr/bin/env bash
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda create -n l8 python=3
                conda activate l8
                pip install numpy twine
                conda install gdal'''
			}
		}		
		stage('Checkout source code') {
			steps {
				sh '''git clone -b develop https://github.com/ESRIN-RSS/L8_reflectance.git'''
			}
		}
		
        stage('Static code analysis') {
        steps {
           script {
              def scannerHome = tool 'Sonar-Scanner';
              withSonarQubeEnv("rss_sonarqube") {
              sh "${scannerHome}/bin/sonar-scanner -X -D sonar.sources=L8_reflectance -D sonar.projectKey=L8reflectance -D sonar.projectName=L8reflectance"
                           }
                   }
               }
            }
	    stage('Functional test code'){
            steps {
                sh '''#!/usr/bin/env bash
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda activate l8
                cd L8_reflectance
                python setup.py install
                cd ..
                chmod +x L8_reflectance/test/automated_tests.sh
                L8_reflectance/test/automated_tests.sh'''
            }
        }
        
        stage("Deploy to test PyPI") {
            steps {
                sh '''#!/usr/bin/env bash
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda activate l8
                twine upload -u vascobnunes -p !MQT!hVx5MjBGdx -r L8_reflectance --repository-url https://test.pypi.org/legacy/ L8_reflectance/dist/*'''
            }
        }

	    stage('Functional test pypi package'){
            steps {
                sh '''#!/usr/bin/env bash
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda activate l8
                pip uninstall L8_reflectance -y
                pip install -i https://test.pypi.org/simple/ L8_reflectance
                chmod +x L8_reflectance/test/automated_tests.sh
                L8_reflectance/test/automated_tests.sh'''
            }
        }
        stage("Deploy to PyPI") {
            steps {
                sh '''#!/usr/bin/env bash
                source $WORKSPACE/miniconda/etc/profile.d/conda.sh
                conda activate l8
                twine upload -u vascobnunes -p !MQT!hVx5MjBGdx -r L8_reflectance --repository-url https://upload.pypi.org/legacy/ L8_reflectance/dist/*'''
            }
        }
    }
    post{
        always {
            cleanWs()
        }
    }
}
