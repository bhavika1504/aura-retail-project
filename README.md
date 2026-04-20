# Aura Retail OS — Path A: Adaptive Autonomous System
**Course:** Object Oriented Programming (IT620)  
**Team:** Devam Tanna · Kajal Varlani · Charmi Bhayani · Bhavika Mulani

---

## System Overview

Aura Retail OS is a modular, event-driven smart-city kiosk platform.  
Every kiosk type (Pharmacy, Food, EmergencyRelief) shares the same hardware  
but operates under different policies driven entirely by design patterns.

---

## How to Run

```bash
# No external dependencies — pure Python 3.8+
python main.py
```

The simulation runs four scenarios automatically and writes transaction logs to `data/`.

---

## Project Structure

```
aura_retail_os/
├── main.py                          ← Simulation entry point
├── events/
│   ├── events.py                    ← Event dataclasses (LowStockEvent, etc.)
│   └── event_bus.py                 ← Observer + Singleton
├── registry/
│   └── central_registry.py          ← Singleton global config + kiosk registry
├── inventory/
│   ├── product.py                   ← Product data model
│   ├── pricing_strategy.py          ← Strategy interface + PricingContext
│   ├── pricing_strategies.py        ← Standard / Discount / Emergency pricing
│   ├── inventory.py                 ← Derived getAvailableStock()
│   └── persistence_manager.py       ← JSON + CSV file I/O
├── hardware/
│   ├── dispenser_hardware.py        ← Spiral / RoboticArm dispensers
│   ├── optional_modules.py          ← RefrigerationUnit, SolarPowerMonitor
│   ├── payment_processor.py         ← Adapter: Card / UPI / Wallet
│   ├── failure_chain.py             ← Chain of Responsibility
│   └── hardware_manager.py          ← Mediator
├── transaction/
│   ├── command.py                   ← Command interface
│   ├── transaction_memento.py       ← Memento snapshot + caretaker
│   ├── commands.py                  ← Purchase / Refund / Restock commands
│   └── command_invoker.py           ← Invoker + undo history + CSV logging
├── core/
│   ├── kiosk_states.py              ← State: Active / PowerSaving / Maintenance / Emergency
│   ├── kiosk_mode_manager.py        ← State context + Strategy host
│   ├── aura_kiosk.py                ← Abstract base kiosk
│   ├── kiosk_types.py               ← Pharmacy / Food / EmergencyRelief
│   └── kiosk_factory.py             ← Abstract Factory
└── interface/
    └── kiosk_interface.py           ← Facade (single external entry point)
```

---

## Implemented Design Patterns

| Pattern | Location | Purpose |
|---|---|---|
| **Facade** | `interface/kiosk_interface.py` | Single simplified API for all external actors |
| **Strategy** | `inventory/pricing_strategies.py` | Runtime-swappable pricing algorithms |
| **State** | `core/kiosk_states.py` | Mode-dependent behaviour without if/elif chains |
| **Command** | `transaction/commands.py` | Encapsulated, undoable operations |
| **Memento** | `transaction/transaction_memento.py` | Atomic rollback snapshot before dispense |
| **Observer** | `events/event_bus.py` | Decoupled event broadcast between subsystems |
| **Chain of Responsibility** | `hardware/failure_chain.py` | Retry → Recalibrate → Alert escalation |
| **Singleton** | `events/event_bus.py`, `registry/central_registry.py` | One global instance per service |
| **Abstract Factory** | `core/kiosk_factory.py` | Compatible component sets per kiosk type |
| **Mediator** | `hardware/hardware_manager.py` | Centralised hardware coordination |
| **Adapter** | `hardware/payment_processor.py` | Unified interface over incompatible payment APIs |

---

## Simulation Scenarios

| # | Scenario | Patterns Exercised |
|---|---|---|
| 1 | Food kiosk normal purchase + live discount pricing | Strategy, Command, Memento, Observer |
| 2 | Emergency kiosk with purchase limits | State (EmergencyState), Abstract Factory |
| 3 | Pharmacy mode transitions | State (all 4 modes), Observer (ModeChangedEvent) |
| 4 | Hardware failure → full recovery chain + hot-swap | Chain of Responsibility, Mediator |

---

## Team Contributions

| Member | Subsystem | Key Files |
|---|---|---|
| **Devam Tanna** (202512010) | Kiosk Core & State Manager | `core/` (all), `interface/kiosk_interface.py` |
| **Kajal Varlani** (202512017) | Transaction & Command Engine | `transaction/` (all) |
| **Charmi Bhayani** (202512028) | Inventory & Adaptive Pricing | `inventory/` (all) |
| **Bhavika Mulani** (202512079) | Hardware HAL & Failure Chain | `hardware/` (all) |

---

## Key Design Decisions

**Derived Attributes** — `Inventory.get_available_stock()` computes  
`quantity - reserved - hw_faulted` live at query time. It is never stored,  
preventing stale reads during concurrent transactions.

**Atomic Transactions** — `PurchaseCommand` saves a `TransactionMemento`  
before calling the dispenser. Any hardware failure triggers an automatic  
refund + inventory release via the memento restore path.

**Zero Direct Coupling** — Subsystems communicate exclusively through  
`EventBus.publish()`. A publisher never imports a subscriber module.

**Hot-swappable Hardware** — `HardwareManager.set_dispenser()` replaces  
the active dispenser at runtime. No business logic changes needed.
