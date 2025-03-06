pipeline {
    agent any

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
        stage('检查环境') {
            steps {
                sh '''
                    # 显示 Docker 版本
                    docker --version

                    # 检查 docker-compose 或 docker compose 是否可用
                    if command -v docker-compose &> /dev/null; then
                        echo "使用 docker-compose 命令"
                        docker-compose --version
                    elif docker compose version &> /dev/null; then
                        echo "使用 docker compose 插件"
                        docker compose version
                    else
                        echo "警告: 未找到 docker-compose 或 docker compose 插件，尝试安装..."
                        # 尝试安装 docker-compose 到用户目录
                        mkdir -p ${HOME}/bin
                        curl -L "https://github.com/docker/compose/releases/download/v2.33.0/docker-compose-$(uname -s)-$(uname -m)" -o ${HOME}/bin/docker-compose
                        chmod +x ${HOME}/bin/docker-compose
                        export PATH="${HOME}/bin:${PATH}"

                        if ${HOME}/bin/docker-compose --version; then
                            echo "docker-compose 安装成功到用户目录"
                            # 创建符号链接到工作目录，以便在脚本中使用
                            ln -sf ${HOME}/bin/docker-compose ${WORKSPACE}/docker-compose
                        else
                            echo "安装 docker-compose 失败，将使用 docker compose 命令"
                        fi
                    fi
                '''
            }
        }

        // stage('安装依赖') {
        //     steps {
        //         sh 'pip install --no-cache-dir -r requirements.txt'
        //         sh 'pip install --no-cache-dir pytest pytest-cov ruff mypy'
        //     }
        // }

        // stage('代码质量检查') {
        //     steps {
        //         sh 'ruff check src/'
        //         sh 'mypy src/'
        //     }
        // }

        stage('Build and Deploy') {
            steps {
                script {
                    // 跳转到指定目录
                    dir("${env.WORKSPACE}") {
                        // 检查 Docker Compose 是否可用，如果不可用则尝试使用 docker compose 命令
                        sh '''
                            # 设置 DOCKER_COMPOSE 变量
                            if command -v docker-compose &> /dev/null; then
                                DOCKER_COMPOSE="docker-compose"
                            elif [ -f "${WORKSPACE}/docker-compose" ] && [ -x "${WORKSPACE}/docker-compose" ]; then
                                DOCKER_COMPOSE="${WORKSPACE}/docker-compose"
                            elif docker compose version &> /dev/null; then
                                DOCKER_COMPOSE="docker compose"
                            else
                                echo "错误: 无法找到可用的 docker-compose 或 docker compose 命令"
                                exit 1
                            fi

                            echo "使用命令: $DOCKER_COMPOSE"

                            # 检查容器是否已存在
                            if $DOCKER_COMPOSE -f deploy/docker-compose.yml ps | grep -q "Up\\|Exit"; then
                                echo "检测到已存在的容器，执行 down 命令..."
                                $DOCKER_COMPOSE -f deploy/docker-compose.yml down
                            else
                                echo "未检测到已存在的容器，直接部署..."
                            fi

                            # 启动容器
                            $DOCKER_COMPOSE -f deploy/docker-compose.yml up -d
                        '''
                    }
                }
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
            sh 'docker system prune -f'
        }

        success {
            // 发送成功通知
            echo '构建成功！'
        }

        failure {
            // 发送失败通知
            echo '构建失败！'
        }
    }
}
