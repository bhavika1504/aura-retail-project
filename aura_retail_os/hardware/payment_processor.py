from abc import ABC, abstractmethod
# =============================================================
# TARGET INTERFACE  (what the kiosk knows)
# =============================================================
class PaymentProcessor(ABC):
    """
    PATTERN: Adapter — Target Interface

    The only payment API the rest of the system ever uses.
    All vendor-specific details are hidden inside adapters.
    """

    @abstractmethod
    def charge(self, amount: float, reference: str) -> bool:
        """Debit the customer. Returns True on success."""

    @abstractmethod
    def refund(self, amount: float, reference: str) -> bool:
        """Credit the customer. Returns True on success."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Human-readable provider label for diagnostics."""


# =============================================================
# ADAPTEES  (incompatible third-party APIs — do NOT modify)
# =============================================================
class CardGatewayAPI:
    """Simulates an incompatible credit-card vendor REST API."""
    def make_payment(self, card_token: str, amount_cents: int) -> dict:
        print(f"[CardGatewayAPI] Charging {amount_cents}¢ via token '{card_token}'")
        return {"status": "SUCCESS", "ref": f"CRD-{card_token[:4].upper()}"}

    def reverse_payment(self, ref: str, amount_cents: int) -> bool:
        print(f"[CardGatewayAPI] Reversing {amount_cents}¢ for ref '{ref}'")
        return True


class UPIVendorAPI:
    """Simulates an incompatible UPI payment SDK."""
    def initiate_upi(self, vpa: str, rupees: float) -> str:
        print(f"[UPIVendorAPI] UPI Rs.{rupees:.2f} → {vpa}")
        return "UPI_SUCCESS"

    def initiate_refund(self, upi_ref: str) -> bool:
        print(f"[UPIVendorAPI] Refund for ref '{upi_ref}'")
        return True


class WalletSDK:
    """Simulates an incompatible digital-wallet mobile SDK."""
    def debit_wallet(self, wallet_id: str, amount: float) -> bool:
        print(f"[WalletSDK] Debiting ₹{amount:.2f} from wallet '{wallet_id}'")
        return True

    def credit_wallet(self, wallet_id: str, amount: float) -> bool:
        print(f"[WalletSDK] Crediting ₹{amount:.2f} to wallet '{wallet_id}'")
        return True


# =============================================================
# ADAPTERS  (bridge adaptee → PaymentProcessor)
# =============================================================
class CardPaymentAdapter(PaymentProcessor):
    """PATTERN: Adapter — wraps CardGatewayAPI → PaymentProcessor."""

    def __init__(self, card_token: str = "XXXX-1234") -> None:
        self._api = CardGatewayAPI()
        self._token = card_token
        self._last_ref: str = ""

    def charge(self, amount: float, reference: str) -> bool:
        result = self._api.make_payment(self._token, int(amount * 100))
        self._last_ref = result.get("ref", reference)
        return result.get("status") == "SUCCESS"

    def refund(self, amount: float, reference: str) -> bool:
        return self._api.reverse_payment(self._last_ref, int(amount * 100))

    def get_provider_name(self) -> str:
        return "CardPayment"


class UPIAdapter(PaymentProcessor):
    """PATTERN: Adapter — wraps UPIVendorAPI → PaymentProcessor."""

    def __init__(self, vpa: str = "user@upi") -> None:
        self._api = UPIVendorAPI()
        self._vpa = vpa
        self._last_ref: str = ""

    def charge(self, amount: float, reference: str) -> bool:
        result = self._api.initiate_upi(self._vpa, amount)
        self._last_ref = reference
        return result == "UPI_SUCCESS"

    def refund(self, amount: float, reference: str) -> bool:
        return self._api.initiate_refund(self._last_ref)

    def get_provider_name(self) -> str:
        return "UPI"


class WalletAdapter(PaymentProcessor):
    """PATTERN: Adapter — wraps WalletSDK → PaymentProcessor."""

    def __init__(self, wallet_id: str = "WALLET-001") -> None:
        self._sdk = WalletSDK()
        self._wallet_id = wallet_id

    def charge(self, amount: float, reference: str) -> bool:
        return self._sdk.debit_wallet(self._wallet_id, amount)

    def refund(self, amount: float, reference: str) -> bool:
        return self._sdk.credit_wallet(self._wallet_id, amount)

    def get_provider_name(self) -> str:
        return "DigitalWallet"
