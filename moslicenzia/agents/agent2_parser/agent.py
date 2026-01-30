import os
import lxml.etree as ET
from typing import Dict, Any, List
from moslicenzia.schemas.models import DocType, AgentResult, ValidationStatus

class ParserAgent:
    """
    Агент 2: Парсер структурированных данных (XML).
    Извлекает ключевые поля из нормализованных XML-документов.
    """
    
    def parse(self, doc_type: DocType, file_path: str) -> AgentResult:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            data = {}
            if doc_type == DocType.APPLICATION:
                data = self._parse_application(root)
            elif doc_type == DocType.EGRUL:
                data = self._parse_egrul(root)
            elif doc_type == DocType.FNS_TAX_DEBT:
                data = self._parse_fns(root)
            elif doc_type == DocType.RNIP_DUTY:
                data = self._parse_rnip(root)
            elif doc_type == DocType.ROSREESTR:
                data = self._parse_rosreestr(root)
            
            return AgentResult(
                agent_id="agent_2",
                doc_id=os.path.basename(file_path),
                status=ValidationStatus.SUCCESS,
                data=data
            )
        except Exception as e:
            import traceback
            return AgentResult(
                agent_id="agent_2",
                doc_id=os.path.basename(file_path),
                status=ValidationStatus.FAILURE,
                comment=f"Extraction Error: {str(e)}\n{traceback.format_exc()}"
            )

    def _parse_application(self, root: ET._Element) -> Dict:
        # На основе "Заявление о выдаче лицензии.xml"
        ns = {"ns": "http://asguf.mos.ru/rkis_gu/coordinate/v6_1/"}
        
        declarant = root.find(".//ns:BaseDeclarant", namespaces=ns)
        if declarant is None:
            return {}

        inn = declarant.findtext("ns:Inn", namespaces=ns)
        kpp = declarant.findtext("ns:Kpp", namespaces=ns)
        name = declarant.findtext("ns:FullName", namespaces=ns)
        
        objects = []
        # Список обособленных подразделений
        for div in root.xpath(".//*[local-name()='separate_division']"):
            objects.append({
                "address": div.findtext(".//pobox") or div.findtext(".//street"),
                "cadastral_number": div.findtext(".//cadastral_number"),
                "name": div.findtext(".//name_unit")
            })
            
        return {
            "inn": inn,
            "kpp": kpp,
            "company_name": name,
            "objects": objects
        }

    def _parse_egrul(self, root: ET._Element) -> Dict:
        # XML ЕГРЮЛ использует атрибуты для ИНН/КПП
        sv_ul_list = root.xpath(".//*[local-name()='СвЮЛ']")
        if not sv_ul_list:
            return {}
        sv_ul = sv_ul_list[0]
            
        inn = sv_ul.get("ИНН")
        kpp = sv_ul.get("КПП")
        
        # Имя находится в СвНаимЮЛ/@НаимЮЛПолн
        name_elem_list = root.xpath(".//*[local-name()='СвНаимЮЛ']")
        name = name_elem_list[0].get("НаимЮЛПолн") if name_elem_list else ""
            
        return {
            "inn": inn,
            "kpp": kpp,
            "company_name": name,
            "status": "ACTIVE"
        }

    def _parse_fns(self, root: ET._Element) -> Dict:
        inf_resp_list = root.xpath(".//*[local-name()='INFZDLResponse']")
        if inf_resp_list:
             has_debt = inf_resp_list[0].get("ПрЗадолж") != "0"
             return {"has_debt_over_3000": has_debt}
        return {"has_debt_over_3000": False}

    def _parse_rnip(self, root: ET._Element) -> Dict:
        info_list = root.xpath(".//*[local-name()='PaymentInfo']")
        amount = 0.0
        if info_list:
            amount_str = info_list[0].get("amount")
            if amount_str:
                amount = float(amount_str) / 100.0
                
        return {"amount": amount, "currency": "RUB"}

    def _parse_rosreestr(self, root: ET._Element) -> Dict:
        cad_num = root.xpath(".//*[local-name()='cad_number']/text()")
        area = root.xpath(".//*[local-name()='area']/text()")
        purpose = root.xpath(".//*[local-name()='purpose']/*[local-name()='value']/text()")
        
        return {
            "cadastral_number": cad_num[0] if cad_num else None,
            "area": area[0] if area else None,
            "purpose": purpose[0] if purpose else None
        }
