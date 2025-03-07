pipeline {
    agent any

    options {
        // 设置构建超时时间为30分钟
        timeout(time: 30, unit: 'MINUTES')
        // 禁用并发构建
        disableConcurrentBuilds()
        // 保留最近10次构建记录
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // 添加时间戳到控制台输出
        timestamps()
        // 设置心跳检查间隔，解决 JENKINS-48300 问题
        durabilityHint('PERFORMANCE_OPTIMIZED')
    }

    environment {
        // 项目名称
        PROJECT_NAME = 'happy_fastapi'
        // Docker镜像名称
        DOCKER_IMAGE = 'happy_fastapi'
        // Docker镜像标签
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        // Docker仓库地址
        DOCKER_REGISTRY = 'dockerhub.sz-alion.com'
        // 部署环境
        DEPLOY_ENV = 'production'
        // 时区设置
        TZ = 'Asia/Shanghai'
    }

    stages {
        stage('安装依赖') {
            steps {
                sh 'pip install --no-cache-dir -r requirements.txt'
                sh 'pip install --no-cache-dir pytest pytest-cov ruff mypy'
            }
        }

        stage('代码质量检查') {
            steps {
                sh 'ruff check src/'
                sh 'mypy src/'
            }
        }

        // stage('单元测试') {
        //     steps {
        //         sh 'pytest --cov=src tests/'
        //     }
        //     post {
        //         always {
        //             junit 'test-reports/*.xml'
        //             publishCoverage adapters: [coberturaAdapter('coverage.xml')]
        //         }
        //     }
        // }

        // stage('构建Docker镜像') {
        //     steps {
        //         sh 'cp .env.${DEPLOY_ENV} .env'
        //         sh 'docker build -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} .'
        //     }
        // }

        // stage('推送Docker镜像') {
        //     steps {
        //         withCredentials([usernamePassword(credentialsId: 'docker-registry-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
        //             sh 'echo ${DOCKER_PASSWORD} | docker login ${DOCKER_REGISTRY} -u ${DOCKER_USERNAME} --password-stdin'
        //             sh 'docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}'
        //             sh 'docker tag ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest'
        //             sh 'docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest'
        //         }
        //     }
        // }

        // stage('部署应用') {
        //     when {
        //         expression { return env.GIT_BRANCH == 'main' || env.GIT_BRANCH == 'master' }
        //     }
        //     steps {
        //         sshagent(['deploy-server-credentials']) {
        //             sh '''
        //                 ssh user@deploy-server "cd /path/to/deployment && \
        //                 export DOCKER_IMAGE=${DOCKER_REGISTRY}/${DOCKER_IMAGE} && \
        //                 export DOCKER_TAG=${DOCKER_TAG} && \
        //                 docker-compose -f deploy/docker-compose.yml pull && \
        //                 docker-compose -f deploy/docker-compose.yml up -d"
        //             '''
        //         }
        //     }
        // }

        // stage('数据库迁移') {
        //     when {
        //         expression { return env.GIT_BRANCH == 'main' || env.GIT_BRANCH == 'master' }
        //     }
        //     steps {
        //         sshagent(['deploy-server-credentials']) {
        //             sh '''
        //                 ssh user@deploy-server "cd /path/to/deployment && \
        //                 docker-compose -f deploy/docker-compose.yml exec -T fastapi_app alembic upgrade head"
        //             '''
        //         }
        //     }
        // }
    }

    post {
        always {
            // 清理工作区
            cleanWs()
            // 清理未使用的Docker镜像
            // sh 'docker system prune -f || true'
        }

        success {
            // 发送成功通知
            echo '构建成功！'
        }

        failure {
            // 发送失败通知
            echo '构建失败！'
        }

        aborted {
            echo '构建被中断！'
        }
    }
}
