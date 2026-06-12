# Shambani Link - Master Blueprint V4

**Mfumo Mkubwa wa Kidijitali wa Kilimo, Ufugaji, Biashara na Fedha Afrika Mashariki**

Shambani Link ni jukwaa pana la kidijitali linalounganisha wadau mbalimbali ili kuleta ufanisi, uaminifu na ukuaji endelevu katika sekta ya agribusiness.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15
- Redis 7
- Elasticsearch 8.11

### Installation

```bash
# Clone repository
git clone https://github.com/patrickntinginya/patrickkid.git
cd patrickkid

# Create environment file
cp .env.example .env

# Update .env with your credentials

# Start all services
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Run migrations (when ready)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Access Points
- API Docs: http://localhost:8000/api/docs
- API ReDoc: http://localhost:8000/api/redoc
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Elasticsearch: localhost:9200

## 📋 Project Structure

```
shambani-link/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/                # Core configurations
│   │   ├── database.py      # PostgreSQL setup
│   │   ├── redis_client.py  # Redis client
│   │   ├── elasticsearch_client.py
│   │   └── security.py      # Authentication & Security
│   ├── models/              # SQLAlchemy models
│   │   └── user.py          # User model
│   ├── api/                 # API routes
│   │   └── routes.py        # All endpoints
│   ├── schemas/             # Pydantic schemas (TBD)
│   └── services/            # Business logic (TBD)
├── scripts/                 # Database scripts
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Services orchestration
├── Dockerfile              # Container configuration
├── .env.example            # Environment template
└── README.md               # This file
```

## 🔧 Core Features

### 1. **Authentication & Users**
- JWT + OTP authentication
- User roles (Farmer, Buyer, Transporter, etc.)
- KYC verification
- Phone & Email verification

### 2. **Marketplace**
- Crop listings
- Livestock marketplace
- Real-time pricing
- Buyer-Seller communication

### 3. **Escrow Payments**
- Secure payment handling
- M-Pesa integration
- Payment verification
- Fraud detection

### 4. **Loans & Finance**
- Crop loans
- Equipment financing
- AI-based credit scoring
- Repayment tracking

### 5. **Insurance**
- Crop insurance
- Livestock insurance
- Weather-indexed insurance
- Claims management

### 6. **Logistics**
- GPS tracking
- Driver ratings
- Route optimization
- Cargo insurance

### 7. **AI Services**
- Crop Doctor (disease detection)
- Livestock Doctor
- Market Forecast
- Financial Scoring
- Voice Assistant (Kiswahili)

### 8. **USSD**
- Menu-driven interface
- SMS notifications
- Mobile money integration
- Offline operation support

## 📚 API Endpoints

### Base URL
```
https://api.shambani-link.com/api/v1
```

### Available Services
- `/auth` - Authentication
- `/users` - User management
- `/marketplace` - Marketplace
- `/escrow` - Escrow payments
- `/loans` - Loan management
- `/insurance` - Insurance policies
- `/logistics` - Logistics & tracking
- `/notifications` - Notifications
- `/ai` - AI services
- `/analytics` - Analytics
- `/payments` - Payment gateway
- `/verification` - User verification
- `/warehouse` - Warehouse management
- `/exports` - Export certificates
- `/ussd` - USSD interface

## 🔐 Security

- JWT authentication with refresh tokens
- OTP verification for sensitive operations
- Password hashing with bcrypt
- Request validation with Pydantic
- CORS protection
- Rate limiting (TBD)
- SQL injection prevention
- XSS protection

## 🗄️ Database

PostgreSQL with SQLAlchemy ORM. Key tables:
- users
- farmers
- crops
- livestock
- orders
- transactions
- escrow_accounts
- loans
- insurance_policies
- transport_requests
- notifications

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app
```

## 📞 Support

For issues and questions:
- GitHub Issues: [shambani-link/issues](https://github.com/patrickntinginya/patrickkid/issues)
- Email: support@shambani-link.com

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributors

- Patrick Ntinginya (@patrickntinginya)

---

**Shambani Link - Kuunganisha, Kuleta Mabadiliko, Kujenga Mafanikio** 🚀
