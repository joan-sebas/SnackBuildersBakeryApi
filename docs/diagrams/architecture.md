# Architecture Diagram

The four layers of the system, the direction of dependencies, and the ports/adapters relationship.

```mermaid
graph TB
    subgraph Interface["Interface Layer (FastAPI)"]
        Routers["Routers"]
        DTOs["Pydantic DTOs"]
        SSE["SSE Endpoints"]
        MW["Middleware"]
    end

    subgraph Application["Application Layer"]
        PlaceOrder["PlaceOrderUseCase"]
        ProcessPayment["ProcessPaymentUseCase"]
        GetStatus["GetOrderStatusUseCase"]
        KitchenState["GetKitchenStateUseCase"]
        MenuMgmt["MenuManagementUseCases"]
    end

    subgraph Domain["Domain Layer (Core — no external deps)"]
        direction TB
        subgraph Entities["Entities and Value Objects"]
            Order["Order"]
            Item["Item"]
            Customer["Customer"]
            MenuItem["MenuItem"]
            Money["Money"]
            Priority["Priority"]
        end
        subgraph Services["Domain Services"]
            Scheduler["KitchenScheduler"]
            PQueue["PriorityQueue"]
            Aging["AgingCalculator"]
        end
        subgraph Ports["Ports (interfaces)"]
            ClockPort["Clock"]
            OrderRepo["OrderRepository"]
            MenuRepo["MenuRepository"]
            PayPort["PaymentProcessor"]
            EventPub["EventPublisher"]
        end
    end

    subgraph Infra["Infrastructure Layer (Adapters)"]
        SqlOrder["SqlAlchemyOrderRepository"]
        SqlMenu["SqlAlchemyMenuRepository"]
        RealClock["RealClock"]
        FakeClock["FakeClock"]
        MockPay["MockPaymentProcessor"]
        EventBus["InMemoryEventBus"]
        BakeTimer["BakeTimer"]
        SlotMonitor["SlotMonitor"]
        Logging["structlog"]
    end

    Interface --> Application
    Application --> Domain
    Infra -.->|implements| Ports
    Interface -.->|reads| Ports

    SqlOrder -.->|implements| OrderRepo
    SqlMenu -.->|implements| MenuRepo
    RealClock -.->|implements| ClockPort
    FakeClock -.->|implements| ClockPort
    MockPay -.->|implements| PayPort
    EventBus -.->|implements| EventPub
```

## The Dependency Rule

Dependencies always point inward toward the domain:

- The **Interface** layer depends on **Application** and on **Domain contracts (Ports)**
- The **Application** layer depends on **Domain**
- The **Infrastructure** layer depends on **Domain** (it implements the ports)
- The **Domain** layer depends on **nothing external**

This means the domain can be tested, refactored, or reused without touching infrastructure or interface concerns. The same domain code would work with a different web framework or a different database.

## Why Ports and Adapters

The ports (interfaces in the domain) define **what** the domain needs. The adapters (implementations in infrastructure) define **how** those needs are met. This separation enables:

- Substituting `FakeClock` for `RealClock` in tests without touching domain code
- Swapping `MockPaymentProcessor` for a real Stripe integration without changes outside infrastructure
- Replacing PostgreSQL with another database by writing new repository adapters
